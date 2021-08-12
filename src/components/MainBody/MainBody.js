import React, { Component } from "react";
import { Layout, Form, Select, Input, Button } from "antd";
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import appRuntime from "../../appRuntime.js";
import "./MainBody.css";

const { Content } = Layout;
const { Option } = Select;

var term = new Terminal();
const fitAddon = new FitAddon();
term.loadAddon(fitAddon);

class MainBody extends Component {
  formRef = React.createRef();
  state = {
    stopButton: false,
    stopButtonDisable: false,
    rows: 20,
    cols: 70,
    ip_library_path: "",
    output_directory: "",
    reportButton: false,
    reportPath: "",
  };

  componentDidMount() {
    // Xterm implementation
    term.setOption("theme", {
      background: "white",
      foreground: "black",
    });
    // Don't want cursor
    term.setOption("cursorStyle", "none");
    term.setOption("cursorBlink", false);
    term.setOption("rendererType", "dom");

    // Open the terminal in #terminal-container
    term.open(document.getElementById("terminal-container"));

    // Make the terminal's size and geometry fit the size of #terminal-container
    fitAddon.fit();
    window.addEventListener("resize", this.handleResize);
    term.onResize((size) => {
      this.setState({ rows: size.rows, cols: size.cols });
    });
  }

  handleResize = () => {
    fitAddon.fit();
  };

  submitValue = (values) => {
    var new_values = values;
    new_values.rows = this.state.rows;
    new_values.cols = this.state.cols;
    if (!this.state.stopButton) {
      this.setState({
        stopButton: true,
        stopButtonDisable: true,
        reportButton: false,
        reportPath: "",
      });
      term.clear();
      appRuntime.subscribe("process.starts", this.ProcessStarts);
      // appRuntime.subscribe("process.report", this.ProcessReport);
      appRuntime.subscribe("terminal.log", this.writeXterm);
      appRuntime.subscribe("process.finish", this.ProcessFinish);
      appRuntime.send("terminal.cmd", new_values);
    } else {
      this.StopHandler();
    }
  };

  ProcessStarts = () => {
    this.setState({ stopButtonDisable: false });
    appRuntime.unsubscribe("process.starts", () => {});
  };

  writeXterm = (data) => {
    term.write(data);
  };

  ProcessFinish = (pid, report_path) => {
    this.setState({ stopButton: false });
    this.ProcessReport(report_path);
    appRuntime.unsubscribe("terminal.log", () => {});
    appRuntime.unsubscribe("process.finish", () => {});
    appRuntime.unsubscribe("process.killed", () => {});
    appRuntime.unsubscribe("process.starts", () => {});
    // appRuntime.unsubscribe("process.report", () => {});
  };

  ProcessReport = (report_path) => {
    if (report_path) {
      this.setState({ reportButton: true, reportPath: report_path });
    }
  };

  ReportOpenar = () => {
    appRuntime.send("report.opener", this.state.reportPath);
  };

  StopHandler = () => {
    this.killProcess();
    // this.setState({ stopButton: false });
  };

  killProcess = () => {
    this.setState({ stopButtonDisable: true });
    appRuntime.send("terminal.kill");
    appRuntime.subscribe("process.killed", this.ProcessKilled);
  };

  ProcessKilled = () => {
    // Handle err if found need to code here
    appRuntime.unsubscribe("process.killed", () => {});
    this.setState({ stopButton: false, stopButtonDisable: false });
  };

  fileSelector = (field_name) => {
    appRuntime.subscribe("selected-file", this.selectedFile);
    appRuntime.send("fileSelector.dialog", field_name);
  };

  selectedFile = (files, field_name, canceled) => {
    if (!canceled) {
      this.setState({ [field_name]: files[0] });
      this.formRef.current.setFieldsValue({ [field_name]: files[0] });
    }
    appRuntime.unsubscribe("selected-file", () => {});
  };

  directorySelector = (field_name) => {
    appRuntime.subscribe("selected-directory", this.selectedDirectory);
    appRuntime.send("directorySelector.dialog", field_name);
  };

  selectedDirectory = (files, field_name, canceled) => {
    if (!canceled) {
      this.setState({ [field_name]: files[0] });
      this.formRef.current.setFieldsValue({ [field_name]: files[0] });
    }
    appRuntime.unsubscribe("selected-directory", () => {});
  };

  handleChange(e) {
    this.setState({ [e.target.dataset.name]: e.target.value });
  }

  render() {
    return (
      <Content className="box" style={{ width: "100%", height: "100%" }}>
        <div className="row header" style={{ width: "100%" }}>
          <div className="Form-Container" style={{ padding: "8px" }}>
            <fieldset
              className="arh-fieldset"
              style={{
                minWidth: "0",
                margin: "0",
                padding: "10px",
                border: "2px solid #9c9c9c",
              }}
            >
              <legend style={{ width: "auto", margin: "0", fontSize: "18px" }}>
                Input
              </legend>
              <Form
                ref={this.formRef}
                name="Pin_Consistency_Check"
                onFinish={this.submitValue}
                labelAlign="left"
                layout="horizontal"
              >
                <Form.Item
                  className={"LabelCol-Custom"}
                  name="IP_Type"
                  label="IP Type"
                  style={{ marginBottom: "6px" }}
                >
                  <Select placeholder="Select IP Type" style={{ width: 150 }}>
                    <Option value="IO">IO</Option>
                    <Option value="MEMORY">MEMORY</Option>
                    <Option value="LOGIC">LOGIC</Option>
                    <Option value="OTHER">OTHER</Option>
                  </Select>
                </Form.Item>
                <Form.Item
                  className={"LabelCol-Custom"}
                  name="ip_library_path"
                  label="IP Library Path"
                  style={{ marginBottom: "6px" }}
                >
                  <div
                    style={{
                      width: "100%",
                      display: "inline-flex",
                      justifyContent: "center",
                    }}
                  >
                    <Input
                      type="text"
                      data-name="ip_library_path"
                      value={this.state.ip_library_path}
                      onChange={this.handleChange.bind(this)}
                    />

                    <Button
                      onClick={() => {
                        this.directorySelector("ip_library_path");
                      }}
                    >
                      Select
                    </Button>
                  </div>
                </Form.Item>
                <Form.Item
                  className={"LabelCol-Custom"}
                  name="output_directory"
                  label="Output Directory"
                  style={{ marginBottom: "6px" }}
                >
                  <div
                    style={{
                      width: "100%",
                      display: "inline-flex",
                      justifyContent: "center",
                    }}
                  >
                    <Input
                      data-name="output_directory"
                      value={this.state.output_directory}
                      onChange={this.handleChange.bind(this)}
                    />

                    <Button
                      onClick={() => {
                        this.directorySelector("output_directory");
                      }}
                    >
                      Select
                    </Button>
                  </div>
                </Form.Item>

                <Form.Item>
                  {this.state.reportButton ? (
                    <Button
                      type="primary"
                      style={{ float: "left" }}
                      onClick={this.ReportOpenar}
                    >
                      Open Report
                    </Button>
                  ) : null}

                  {this.state.stopButton ? (
                    <Button
                      type="danger"
                      htmlType="submit"
                      disabled={this.state.stopButtonDisable}
                      style={{ float: "right" }}
                    >
                      Stop
                    </Button>
                  ) : (
                    <Button
                      type="primary"
                      htmlType="submit"
                      style={{ float: "right" }}
                    >
                      RUN
                    </Button>
                  )}
                </Form.Item>
              </Form>
            </fieldset>
          </div>
        </div>
        <div
          className="row content"
          style={{
            width: "100%",
            padding: "0px 8px 8px 8px",
            overflow: "hidden",
          }}
        >
          <fieldset
            className="arh-fieldset"
            style={{
              minWidth: "0",
              margin: "0",
              padding: "10px",
              border: "2px solid #9c9c9c",
              width: "100%",
              height: "100%",
            }}
          >
            <legend style={{ width: "auto", margin: "0", fontSize: "18px" }}>
              Output
            </legend>
            <div
              id={"terminal-container"}
              style={{
                width: "100%",
                height: "100%",

                overflow: "hidden",
              }}
            ></div>
          </fieldset>
        </div>
      </Content>
    );
  }
}

export default MainBody;
