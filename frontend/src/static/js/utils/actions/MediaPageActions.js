import Dispatcher from '../dispatcher.js';

export function loadMediaData() {
  Dispatcher.dispatch({
    type: 'LOAD_MEDIA_DATA',
  });
}

export function copyShareLink(inputElem) {
  Dispatcher.dispatch({
    type: 'COPY_SHARE_LINK',
    inputElement: inputElem,
  });
}

export function copyEmbedMediaCode(inputElem) {
  Dispatcher.dispatch({
    type: 'COPY_EMBED_MEDIA_CODE',
    inputElement: inputElem,
  });
}

export function removeMedia() {
  Dispatcher.dispatch({
    type: 'REMOVE_MEDIA',
  });
}

export function createPlaylist(playlist_data) {
  Dispatcher.dispatch({
    type: 'CREATE_PLAYLIST',
    playlist_data,
  });
}

export function addMediaToPlaylist(playlist_id, media_id) {
  Dispatcher.dispatch({
    type: 'ADD_MEDIA_TO_PLAYLIST',
    playlist_id,
    media_id,
  });
}

export function removeMediaFromPlaylist(playlist_id, media_id) {
  Dispatcher.dispatch({
    type: 'REMOVE_MEDIA_FROM_PLAYLIST',
    playlist_id,
    media_id,
  });
}

export function addNewPlaylist(playlist_data) {
  Dispatcher.dispatch({
    type: 'APPEND_NEW_PLAYLIST',
    playlist_data,
  });
}

