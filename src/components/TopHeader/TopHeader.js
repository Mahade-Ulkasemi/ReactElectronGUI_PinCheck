import React, { Component } from "react";
import { Layout } from "antd";
import "./TopHeader.css";

const { Header } = Layout;
class TopHeader extends Component {
  state = {};
  render() {
    return (
      <Header className="TopHeader">
        <div className="TopHeader-Title">
          <h3>Std Cell Library Pin Consistency Check & Report Generator</h3>
        </div>
      </Header>
    );
  }
}

export default TopHeader;
