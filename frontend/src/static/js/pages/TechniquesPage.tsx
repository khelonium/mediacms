import React, { useEffect, useState } from 'react';
import { Page } from './Page';
import './TechniquesPage.scss';

declare global {
  interface Window {
    MediaCMS: any;
  }
}

interface Resource {
  url: string;
  source: string;
  seed_title?: string;
}

interface TechniqueMediaItem {
  friendly_token: string;
  title: string;
  thumbnail_url: string | null;
  url: string;
}

interface TechniqueNode {
  id: string;
  title: string;
  status?: string;
  notes?: string | null;
  resources?: Resource[];
  media?: TechniqueMediaItem[];
  children?: TechniqueNode[];
}

interface TechniquesData {
  version: number;
  tree: TechniqueNode[];
}

function MediaItems({ media }: { media: TechniqueMediaItem[] }) {
  return (
    <>
      {media.map((m) => (
        <li key={m.friendly_token} className="techniques-item">
          <span className="techniques-item-title">{m.title}</span>
          <span className="techniques-resources">
            <a href={m.url} className="techniques-link">Watch</a>
          </span>
        </li>
      ))}
    </>
  );
}

function TechniqueItem({ node, depth }: { node: TechniqueNode; depth: number }) {
  const hasChildren = node.children && node.children.length > 0;
  const hasResources = node.resources && node.resources.length > 0;
  const hasMedia = node.media && node.media.length > 0;
  const mediaItems = hasMedia ? node.media! : [];
  const childItems = hasChildren ? node.children! : [];

  if (depth === 0) {
    const hasContent = mediaItems.length > 0 || childItems.length > 0;
    return (
      <div className="techniques-category">
        <h2 className="techniques-category-title">{node.title}</h2>
        {hasContent && (
          <div className="techniques-category-children">
            {mediaItems.length > 0 && (
              <ul className="techniques-list">
                <MediaItems media={mediaItems} />
              </ul>
            )}
            {childItems.map((child) => (
              <TechniqueItem key={child.id} node={child} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  }

  if (depth === 1) {
    const hasContent = mediaItems.length > 0 || childItems.length > 0;
    return (
      <div className="techniques-subcategory">
        <h3 className="techniques-subcategory-title">{node.title}</h3>
        {node.notes && <span className="techniques-notes">{node.notes}</span>}
        {hasContent && (
          <ul className="techniques-list">
            <MediaItems media={mediaItems} />
            {childItems.map((child) => (
              <TechniqueItem key={child.id} node={child} depth={depth + 1} />
            ))}
          </ul>
        )}
      </div>
    );
  }

  if (depth === 2 && hasChildren && !node.status) {
    return (
      <li className="techniques-sub-subcategory">
        <h4 className="techniques-sub-subcategory-title">{node.title}</h4>
        <ul className="techniques-list">
          <MediaItems media={mediaItems} />
          {childItems.map((child) => (
            <TechniqueItem key={child.id} node={child} depth={depth + 1} />
          ))}
        </ul>
      </li>
    );
  }

  return (
    <li className="techniques-item">
      <span className="techniques-item-title">{node.title}</span>
      {node.notes && <span className="techniques-notes"> — {node.notes}</span>}
      {hasResources && (
        <span className="techniques-resources">
          {node.resources!.map((r, i) => (
            <a key={i} href={r.url} target="_blank" rel="noopener noreferrer" className="techniques-link" title={r.seed_title || undefined}>
              {r.seed_title || node.title}
            </a>
          ))}
        </span>
      )}
      {hasMedia && (
        <ul className="techniques-list">
          <MediaItems media={mediaItems} />
        </ul>
      )}
      {hasChildren && (
        <ul className="techniques-list">
          {childItems.map((child) => (
            <TechniqueItem key={child.id} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}

export const TechniquesPage: React.FC = () => {
  const [data, setData] = useState<TechniquesData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v1/techniques', { credentials: 'include' })
      .then((res) => {
        if (res.status === 403) {
          setError('You do not have access to this page.');
          setLoading(false);
          return null;
        }
        if (!res.ok) {
          setError('Failed to load techniques.');
          setLoading(false);
          return null;
        }
        return res.json();
      })
      .then((json) => {
        if (json) {
          setData(json);
          setLoading(false);
        }
      })
      .catch(() => {
        setError('Failed to load techniques.');
        setLoading(false);
      });
  }, []);

  let content;
  if (loading) {
    content = <p>Loading techniques...</p>;
  } else if (error) {
    content = <p className="techniques-error">{error}</p>;
  } else if (data) {
    const total = data.tree.reduce((acc, cat) => {
      const countNodes = (n: TechniqueNode): number => {
        const childCount = n.children ? n.children.reduce((a, c) => a + countNodes(c), 0) : 0;
        return (n.status ? 1 : 0) + childCount;
      };
      return acc + countNodes(cat);
    }, 0);

    content = (
      <div className="techniques-tree">
        <p className="techniques-summary">{total} techniques</p>
        {data.tree.map((cat) => (
          <TechniqueItem key={cat.id} node={cat} depth={0} />
        ))}
      </div>
    );
  }

  return (
    <Page id="techniques">
      <div className="techniques-page">
        <h1>Techniques</h1>
        {content}
      </div>
    </Page>
  );
};
