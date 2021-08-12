import logo from "./logo.svg";
import "./App.css";
import { Layout } from "antd";
import TopHeader from "./components/TopHeader/TopHeader";
import MainBody from "./components/MainBody/MainBody";

const { Content } = Layout;

function App() {
  return (
    <>
      <Layout
        style={{ width: "100%", height: "100%", backgroundColor: "#d9d9d9" }}
      >
        <TopHeader />

        <MainBody />
      </Layout>
    </>
  );
}

export default App;
