import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

import AdminManagementPage from "@/pages/AdminManagementPage";
import ChatPage from "@/pages/ChatPage";

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/chat" replace />} />
        <Route path="/chat" element={<ChatPage />} />
        <Route path="/admin/settings" element={<AdminManagementPage />} />
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
