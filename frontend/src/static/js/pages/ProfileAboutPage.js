import React from 'react';
import PropTypes from 'prop-types';
import UrlParse from 'url-parse';
import { SiteContext } from '../utils/contexts/';
import { formatInnerLink } from '../utils/helpers/';
import { PageStore } from '../utils/stores/';
import ProfilePagesHeader from '../components/profile-page/ProfilePagesHeader';
import ProfilePagesContent from '../components/profile-page/ProfilePagesContent';
import { MediaListRow } from '../components/MediaListRow';
import { ProfileMediaPage } from './ProfileMediaPage';

export class ProfileAboutPage extends ProfileMediaPage {
  constructor(props) {
    super(props, 'author-about');

  }

  pageContent() {
    let description = null;
    let details = [];
    let socialMedia = [];

    if (this.state.author) {
      let i;

      if (
        void 0 !== this.state.author.description &&
        !!this.state.author.description &&
        '' !== this.state.author.description
      ) {
        description = this.state.author.description;
      }

      if (void 0 !== this.state.author.location_info && this.state.author.location_info.length) {
        let locations = [];
        i = 0;
        while (i < this.state.author.location_info.length) {
          if (
            void 0 !== this.state.author.location_info[i].title &&
            void 0 !== this.state.author.location_info[i].url
          ) {
            locations.push(
              <a
                key={i}
                href={formatInnerLink(this.state.author.location_info[i].url, SiteContext._currentValue.url)}
                title={this.state.author.location_info[i].title}
              >
                {this.state.author.location_info[i].title}
              </a>
            );
          }
          i += 1;
        }
        details.push(
          <li key={'location'}>
            <span>Location:</span>
            <span>{locations}</span>
          </li>
        );
      } else if (
        void 0 !== this.state.author.location &&
        !!this.state.author.location &&
        '' !== this.state.author.location
      ) {
        // TODO: Remove it, doesn't really need. Remains for backward compatibility.
        details.push(
          <li key={'location'}>
            <span>Location:</span>
            <span>{this.state.author.location}</span>
          </li>
        );
      }

      let lnk;

      if (
        void 0 !== this.state.author.home_page &&
        !!this.state.author.home_page &&
        '' !== this.state.author.home_page
      ) {
        lnk = UrlParse(this.state.author.home_page.trim()).toString();
        if ('' !== lnk) {
          details.push(
            <li key={'website'}>
              <span>Website:</span>
              <span>{lnk}</span>
            </li>
          );
        }
      }

      if (
        void 0 !== this.state.author.social_media_links &&
        !!this.state.author.social_media_links &&
        '' !== this.state.author.social_media_links
      ) {
        let socialMediaLinks = this.state.author.social_media_links.split(',');
        if (socialMediaLinks.length) {
          i = 0;
          while (i < socialMediaLinks.length) {
            lnk = socialMediaLinks[i].trim();
            if ('' !== lnk) {
              socialMedia.push(<span key={i}>{lnk}</span>);
            }
            i += 1;
          }
          details.push(
            <li key={'social_media'}>
              <span>Social media:</span>
              <span className="author-social-media">{socialMedia}</span>
            </li>
          );
        }
      }
    }

    return [
      this.state.author ? (
        <ProfilePagesHeader key="ProfilePagesHeader" author={this.state.author} type="about" />
      ) : null,
      this.state.author ? (
        <ProfilePagesContent key="ProfilePagesContent">
          <div className="media-list-wrapper items-list-ver  profile-about-content ">
            {null === description && 0 < details.length ? null : PageStore.get('config-options').pages.profile
                .htmlInDescription ? (
              <MediaListRow title={this.props.title}>
                <span dangerouslySetInnerHTML={{ __html: description || null }}></span>
              </MediaListRow>
            ) : (
              <MediaListRow title={this.props.title}>{description}</MediaListRow>
            )}

            {!details.length ? null : (
              <MediaListRow title={'Details'}>
                <ul className="profile-details">{details}</ul>
              </MediaListRow>
            )}

          </div>
        </ProfilePagesContent>
      ) : null,
    ];
  }
}

ProfileAboutPage.propTypes = {
  title: PropTypes.string.isRequired,
};

ProfileAboutPage.defaultProps = {
  title: 'Biography',
};
