import { Navigate, Route, Routes } from "react-router-dom";

import AdminManagementPage from "../pages/AdminManagementPage";

const AppRouter = () => {
  return (
    <Routes>
      <Route path="/admin/settings" element={<AdminManagementPage />} />
      <Route path="*" element={<Navigate replace to="/admin/settings" />} />
    </Routes>
  );
};

export default AppRouter;
