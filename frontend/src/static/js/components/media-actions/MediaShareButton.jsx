import React from 'react';
import { usePopup } from '../../utils/hooks/';
import { CircleIconButton, MaterialIcon, PopupMain } from '../_shared/';
import { MediaShareOptions } from './MediaShareOptions';

export function MediaShareButton() {
  const [popupContentRef, PopupContent, PopupTrigger] = usePopup();

  return (
    <div className="share">
      <PopupTrigger contentRef={popupContentRef}>
        <button>
          <CircleIconButton type="span">
            <MaterialIcon type="share" />
          </CircleIconButton>
          <span>SHARE</span>
        </button>
      </PopupTrigger>

      <PopupContent contentRef={popupContentRef}>
        <div className="popup-fullscreen">
          <PopupMain>
            <span className="popup-fullscreen-overlay"></span>
            <MediaShareOptions />
          </PopupMain>
        </div>
      </PopupContent>
    </div>
  );
}
