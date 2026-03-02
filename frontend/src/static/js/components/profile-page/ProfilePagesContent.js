import React from 'react';

export default class ProfilePagesContent extends React.PureComponent {
  render() {
    return this.props.children ? (
      <div className="profile-page-content">
        {this.props.children}
      </div>
    ) : null;
  }
}
