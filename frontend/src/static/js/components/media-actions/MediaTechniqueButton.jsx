import React, { useState } from 'react';
import { usePopup } from '../../utils/hooks/';
import { CircleIconButton, MaterialIcon, NavigationContentApp, PopupMain } from '../_shared/';
import { TechniqueSelection } from '../technique-selection/TechniqueSelection';

function techniqueSavePopupPages(onTriggerPopupClose) {
  return {
    selectTechnique: (
      <div className="popup-fullscreen">
        <PopupMain>
          <span className="popup-fullscreen-overlay"></span>
          <TechniqueSelection triggerPopupClose={onTriggerPopupClose} />
        </PopupMain>
      </div>
    ),
  };
}

export function MediaTechniqueButton(props) {
  const [popupContentRef, PopupContent, PopupTrigger] = usePopup();

  const [popupCurrentPage, setPopupCurrentPage] = useState('selectTechnique');

  function triggerPopupClose() {
    popupContentRef.current.toggle();
  }

  return (
    <div className="technique">
      <PopupTrigger contentRef={popupContentRef}>
        <button>
          <CircleIconButton type="span">
            <MaterialIcon type="fitness_center" />
          </CircleIconButton>
          <span>TECHNIQUE</span>
        </button>
      </PopupTrigger>

      <PopupContent contentRef={popupContentRef}>
        <NavigationContentApp
          initPage={popupCurrentPage}
          pageChangeSelector={'.change-page'}
          pageIdSelectorAttr={'data-page-id'}
          pages={techniqueSavePopupPages(triggerPopupClose)}
          focusFirstItemOnPageChange={false}
          pageChangeCallback={setPopupCurrentPage}
        />
      </PopupContent>
    </div>
  );
}
