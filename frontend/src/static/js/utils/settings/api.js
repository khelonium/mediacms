const urlParse = require('url-parse');

let BASE_URL = null;
let ENDPOINTS = null;

function endpointsIter(ret, endpoints) {
  const baseUrl = BASE_URL.toString().replace(/\/+$/, '');

  for (let k in endpoints) {
    if ('string' === typeof endpoints[k]) {
      ret[k] = baseUrl + '/' + endpoints[k].replace(/^\//g, '');
    } else {
      endpointsIter(ret[k], endpoints[k]);
    }
  }
}

function formatEndpoints(endpoints) {
  const baseUrl = BASE_URL.toString();
  const ret = endpoints;
  endpointsIter(ret, endpoints);
  return ret;
}

export function init(base_url, endpoints) {
  BASE_URL = urlParse(base_url);

  ENDPOINTS = formatEndpoints({
    media: endpoints.media,
    playlists: endpoints.playlists,
    user: {
      history: endpoints.history,
      playlists: endpoints.playlists + '?author=',
    },
    archive: {
      tags: endpoints.tags,
      categories: endpoints.categories,
    },
    search: {
      query: endpoints.search + '?q=',
      titles: endpoints.search + '?show=titles&q=',
      tag: endpoints.search + '?t=',
      category: endpoints.search + '?c=',
    },
  });
}

export function endpoints() {
  return ENDPOINTS;
}
