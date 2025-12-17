function Sidebar() {
  return (
    <div className="sidebar">
      <h2 className="sidebar-title">Workspace</h2>

      <ul className="sidebar-menu">
        <li>📄 Reports</li>
        <li>🕘 History</li>
        <li>⭐ Favorites</li>
        <li>⚙ Settings</li>
      </ul>

      <div className="sidebar-section">
        <h4>RECENT REPORTS</h4>
        <div className="recent-item">
          <strong>Q4 Market Analysis</strong>
          <span>15/01/2024</span>
        </div>
        <div className="recent-item">
          <strong>Financial Performance</strong>
          <span>14/01/2024</span>
        </div>
        <div className="recent-item">
          <strong>Customer Insights</strong>
          <span>13/01/2024</span>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
