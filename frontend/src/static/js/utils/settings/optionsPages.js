let PAGES = null;

export function init(home, search, media, profile, VALID_PAGES) {
  PAGES = {
    home: {
      sections: {
        latest: {
          title: '',
        },
      },
    },
    search: {
      advancedFilters: false,
    },
    media: {
      categoriesWithTitle: false,
      htmlInDescription: false,
      displayViews: true,
      related: {
        initialSize: 10,
      },
    },
    profile: {
      htmlInDescription: false,
      includeHistory: false,
    },
  };

  if (void 0 !== home) {
    if (void 0 !== home.sections) {
      if (void 0 !== home.sections.latest) {
        if ('string' === typeof home.sections.latest.title) {
          PAGES.home.sections.latest.title = home.sections.latest.title.trim();
        }
      }

    }
  }

  if (void 0 !== search) {
    if (true === search.advancedFilters) {
      PAGES.search.advancedFilters = search.advancedFilters;
    }
  }

  if ('' === PAGES.home.sections.latest.title) {
    PAGES.home.sections.latest.title = void 0 !== VALID_PAGES.latest ? VALID_PAGES.latest.title : 'Latest';
  }

  if (void 0 !== media) {
    if (true === media.categoriesWithTitle) {
      PAGES.media.categoriesWithTitle = media.categoriesWithTitle;
    }

    if (true === media.hideViews) {
      PAGES.media.displayViews = false;
    }

    if (true === media.htmlInDescription) {
      PAGES.media.htmlInDescription = media.htmlInDescription;
    }
  }

  if (void 0 !== profile) {
    if (true === profile.htmlInDescription) {
      PAGES.profile.htmlInDescription = profile.htmlInDescription;
    }

    if (true === profile.includeHistory) {
      PAGES.profile.includeHistory = profile.includeHistory;
    }

  }
}

export function settings() {
  return PAGES;
}
