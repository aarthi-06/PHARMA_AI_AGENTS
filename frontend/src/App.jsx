import Sidebar from "./components/Sidebar";
import ReportGenerator from "./components/ReportGenerator";
import "./index.css";

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <ReportGenerator />
    </div>
  );
}

export default App;
