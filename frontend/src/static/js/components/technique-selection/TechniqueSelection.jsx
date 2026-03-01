import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { MediaPageStore } from '../../utils/stores/';
import { PageActions, MediaPageActions } from '../../utils/actions/';
import { CircleIconButton, MaterialIcon } from '../_shared';

import './TechniqueSelection.scss';

export function TechniqueSelection(props) {
  const containerRef = useRef(null);

  const [tree, setTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedSubcategory, setSelectedSubcategory] = useState('');
  const [techniqueTitle, setTechniqueTitle] = useState('');
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newSubcategoryName, setNewSubcategoryName] = useState('');
  const [creatingCategory, setCreatingCategory] = useState(false);
  const [creatingSubcategory, setCreatingSubcategory] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  function onTechniqueTreeLoaded() {
    setTree(MediaPageStore.get('technique-tree'));
    setLoading(false);
  }

  function onTechniqueTreeLoadFailed() {
    setLoading(false);
  }

  function onTechniqueMediaAdditionCompleted() {
    setSubmitting(false);
    setTimeout(function () {
      PageActions.addNotification('Video added to technique', 'techniqueMediaAdditionComplete');
    }, 100);
    if (void 0 !== props.triggerPopupClose) {
      props.triggerPopupClose();
    }
  }

  function onTechniqueMediaAdditionFailed() {
    setSubmitting(false);
    setTimeout(function () {
      PageActions.addNotification('Failed to add video to technique', 'techniqueMediaAdditionFail');
    }, 100);
  }

  function onTechniqueMediaAlreadyAdded() {
    setSubmitting(false);
    setTimeout(function () {
      PageActions.addNotification('This video is already added to this technique', 'techniqueMediaAlreadyAdded');
    }, 100);
  }

  useEffect(() => {
    // Pre-fill title from media data
    const mediaData = MediaPageStore.get('media-data');
    if (mediaData && mediaData.title) {
      setTechniqueTitle(mediaData.title);
    }

    MediaPageStore.on('technique_tree_loaded', onTechniqueTreeLoaded);
    MediaPageStore.on('technique_tree_load_failed', onTechniqueTreeLoadFailed);
    MediaPageStore.on('technique_media_addition_completed', onTechniqueMediaAdditionCompleted);
    MediaPageStore.on('technique_media_addition_failed', onTechniqueMediaAdditionFailed);
    MediaPageStore.on('technique_media_already_added', onTechniqueMediaAlreadyAdded);

    MediaPageActions.loadTechniqueTree();

    return () => {
      MediaPageStore.removeListener('technique_tree_loaded', onTechniqueTreeLoaded);
      MediaPageStore.removeListener('technique_tree_load_failed', onTechniqueTreeLoadFailed);
      MediaPageStore.removeListener('technique_media_addition_completed', onTechniqueMediaAdditionCompleted);
      MediaPageStore.removeListener('technique_media_addition_failed', onTechniqueMediaAdditionFailed);
      MediaPageStore.removeListener('technique_media_already_added', onTechniqueMediaAlreadyAdded);
    };
  }, []);

  function getSubcategories() {
    if (!selectedCategory) return [];
    const cat = tree.find(function (c) {
      return c.id === selectedCategory;
    });
    return cat && cat.children ? cat.children : [];
  }

  function getTechniqueId() {
    if (selectedSubcategory) {
      return selectedSubcategory;
    }
    if (selectedCategory) {
      return selectedCategory;
    }
    return '';
  }

  function createCategoryRequest(title, parentId) {
    var body = { title: title };
    if (parentId) {
      body.parent_id = parentId;
    }
    return fetch('/api/v1/techniques/categories', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify(body),
    }).then(function (res) { return res.json(); });
  }

  function onSubmit() {
    if (!techniqueTitle.trim()) return;

    setSubmitting(true);
    var mediaId = MediaPageStore.get('media-id');
    var title = techniqueTitle.trim();

    // Case 1: New category typed but not yet created
    if (newCategoryName.trim() && !selectedCategory) {
      createCategoryRequest(newCategoryName.trim())
        .then(function (catData) {
          if (!catData.id) { throw new Error('Category creation failed'); }
          setNewCategoryName('');
          setSelectedCategory(catData.id);
          MediaPageActions.loadTechniqueTree();

          // If there's also a new subcategory name, create it under the new category
          if (newSubcategoryName.trim()) {
            return createCategoryRequest(newSubcategoryName.trim(), catData.id).then(function (subData) {
              if (!subData.id) { throw new Error('Subcategory creation failed'); }
              setNewSubcategoryName('');
              setSelectedSubcategory(subData.id);
              MediaPageActions.loadTechniqueTree();
              return subData.id;
            });
          }
          return catData.id;
        })
        .then(function (techniqueId) {
          MediaPageActions.addMediaToTechnique(techniqueId, mediaId, title);
        })
        .catch(function () {
          setSubmitting(false);
          PageActions.addNotification('Failed to create category', 'categoryCreationFail');
        });
      return;
    }

    // Case 2: Category selected, new subcategory typed but not yet created
    if (selectedCategory && newSubcategoryName.trim() && !selectedSubcategory) {
      createCategoryRequest(newSubcategoryName.trim(), selectedCategory)
        .then(function (subData) {
          if (!subData.id) { throw new Error('Subcategory creation failed'); }
          setNewSubcategoryName('');
          setSelectedSubcategory(subData.id);
          MediaPageActions.loadTechniqueTree();
          MediaPageActions.addMediaToTechnique(subData.id, mediaId, title);
        })
        .catch(function () {
          setSubmitting(false);
          PageActions.addNotification('Failed to create subcategory', 'subcategoryCreationFail');
        });
      return;
    }

    // Case 3: Everything already selected
    var techniqueId = getTechniqueId();
    if (!techniqueId) return;
    MediaPageActions.addMediaToTechnique(techniqueId, mediaId, title);
  }

  function onCreateCategory() {
    if (!newCategoryName.trim()) return;
    setCreatingCategory(true);

    fetch('/api/v1/techniques/categories', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ title: newCategoryName.trim() }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        setCreatingCategory(false);
        setNewCategoryName('');
        // Reload tree
        MediaPageActions.loadTechniqueTree();
        if (data.id) {
          setSelectedCategory(data.id);
        }
      })
      .catch(function () {
        setCreatingCategory(false);
      });
  }

  function onCreateSubcategory() {
    if (!newSubcategoryName.trim() || !selectedCategory) return;
    setCreatingSubcategory(true);

    fetch('/api/v1/techniques/categories', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCsrfToken(),
      },
      body: JSON.stringify({ parent_id: selectedCategory, title: newSubcategoryName.trim() }),
    })
      .then(function (res) { return res.json(); })
      .then(function (data) {
        setCreatingSubcategory(false);
        setNewSubcategoryName('');
        MediaPageActions.loadTechniqueTree();
        if (data.id) {
          setSelectedSubcategory(data.id);
        }
      })
      .catch(function () {
        setCreatingSubcategory(false);
      });
  }

  function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
  }

  function onClickExit() {
    if (void 0 !== props.triggerPopupClose) {
      props.triggerPopupClose();
    }
  }

  function onCategoryChange(ev) {
    setSelectedCategory(ev.target.value);
    setSelectedSubcategory('');
  }

  const subcategories = getSubcategories();
  const hasPendingCategory = newCategoryName.trim() && !selectedCategory;
  const hasPendingSubcategory = selectedCategory && newSubcategoryName.trim() && !selectedSubcategory;
  const hasTarget = getTechniqueId() || hasPendingCategory || hasPendingSubcategory;
  const canSubmit = hasTarget && techniqueTitle.trim() && !submitting;

  return (
    <div ref={containerRef} className="technique-popup">
      <div className="technique-title">
        Add to Techniques
        <CircleIconButton type="button" onClick={onClickExit}>
          <MaterialIcon type="close" />
        </CircleIconButton>
      </div>

      {loading ? (
        <div className="technique-loading">Loading...</div>
      ) : (
        <div className="technique-form">
          <div className="technique-field">
            <label>Category</label>
            <select value={selectedCategory} onChange={onCategoryChange}>
              <option value="">Select category...</option>
              {tree.map(function (cat) {
                return (
                  <option key={cat.id} value={cat.id}>
                    {cat.title}
                  </option>
                );
              })}
            </select>
            <div className="technique-create-new">
              <input
                type="text"
                placeholder="New category name..."
                value={newCategoryName}
                onChange={function (e) { setNewCategoryName(e.target.value); }}
              />
              <button onClick={onCreateCategory} disabled={creatingCategory || !newCategoryName.trim()}>
                {creatingCategory ? '...' : 'Create'}
              </button>
            </div>
          </div>

          {selectedCategory ? (
            <div className="technique-field">
              <label>Subcategory</label>
              <select
                value={selectedSubcategory}
                onChange={function (ev) { setSelectedSubcategory(ev.target.value); }}
              >
                <option value="">Select subcategory...</option>
                {subcategories.map(function (sub) {
                  return (
                    <option key={sub.id} value={sub.id}>
                      {sub.title}
                    </option>
                  );
                })}
              </select>
              <div className="technique-create-new">
                <input
                  type="text"
                  placeholder="New subcategory name..."
                  value={newSubcategoryName}
                  onChange={function (e) { setNewSubcategoryName(e.target.value); }}
                />
                <button onClick={onCreateSubcategory} disabled={creatingSubcategory || !newSubcategoryName.trim()}>
                  {creatingSubcategory ? '...' : 'Create'}
                </button>
              </div>
            </div>
          ) : null}

          <div className="technique-field">
            <label>Technique title</label>
            <input
              type="text"
              value={techniqueTitle}
              onChange={function (e) { setTechniqueTitle(e.target.value); }}
              placeholder="Technique title..."
            />
          </div>

          <button className="technique-submit" onClick={onSubmit} disabled={!canSubmit}>
            {submitting ? 'Adding...' : 'Add to Techniques'}
          </button>
        </div>
      )}
    </div>
  );
}

TechniqueSelection.propTypes = {
  triggerPopupClose: PropTypes.func,
};
