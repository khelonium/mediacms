import * as api from './api.js';
import * as media from './media.js';
import * as site from './site.js';
import * as theme from './theme.js';
import * as url from './url.js';
import * as member from './member.js';
import * as contents from './contents.js';
import * as pages from './pages.js';
import * as sidebar from './sidebar.js';
import * as taxonomies from './taxonomies.js';
import * as optionsPages from './optionsPages.js';
import * as playlists from './playlists.js';
import * as notifications from './notifications.js';

let DATA = null;

export function config(glbl) {
  if (DATA) {
    return DATA;
  }

  pages.init({ ...glbl.site.pages, ...glbl.site.userPages });
  optionsPages.init(glbl.pages.home, glbl.pages.search, glbl.pages.media, glbl.pages.profile, pages.settings());

  url.init({
    home: glbl.url.home,
    admin: !glbl.user.is.anonymous && glbl.user.is.admin ? glbl.url.admin : '',
    error404: glbl.url.error404,
    latest: glbl.url.latestMedia,
    signin: glbl.url.signin,
    signout: !glbl.user.is.anonymous ? glbl.url.signout : '',
    register: glbl.url.register,
    changePassword: !glbl.user.is.anonymous ? glbl.url.changePassword : '',
    search: {
      base: glbl.url.search,
      query: glbl.url.search + '?q=',
      tag: glbl.url.search + '?t=',
      category: glbl.url.search + '?c=',
    },
    profile: !!glbl.site.devEnv
      ? {
          media: glbl.user.pages.media,
          about: glbl.user.pages.about,
          playlists: glbl.user.pages.playlists,
        }
      : {
          media: glbl.site.url.replace(/\/$/, '') + '/user/' + glbl.profileId,
          about: glbl.site.url.replace(/\/$/, '') + '/user/' + glbl.profileId + '/about',
          playlists: glbl.site.url.replace(/\/$/, '') + '/user/' + glbl.profileId + '/playlists',
        },
    user: {
      history: glbl.url.history,
      addMedia: glbl.url.addMedia,
      editChannel: glbl.url.editChannel,
      editProfile: glbl.url.editProfile,
      techniques: glbl.url.techniques || '',
    },
    archive: {
      tags: glbl.url.tags,
      categories: glbl.url.categories,
    },
  });

  site.init(glbl.site);
  contents.init(glbl.contents);
  api.init(glbl.site.api, glbl.api);
  sidebar.init(glbl.features.sideBar);
  taxonomies.init(glbl.site.taxonomies);
  member.init(glbl.user, glbl.features);
  theme.init(glbl.site.theme, glbl.site.logo);
  media.init(glbl.features.mediaItem, glbl.features.media.shareOptions);
  playlists.init(glbl.features.playlists);

  notifications.init(glbl.contents.notifications);

  DATA = {
    site: site.settings(),
    theme: theme.settings(),
    member: member.settings(),
    media: media.settings(),
    playlists: playlists.settings(),
    url: url.pages(),
    api: api.endpoints(),
    sidebar: sidebar.settings(),
    contents: contents.settings(),
    options: {
      pages: optionsPages.settings(),
    },
    enabled: {
      pages: pages.settings(),
      taxonomies: taxonomies.settings(),
    },
    notifications: notifications.settings(),
  };

  return DATA;
}
