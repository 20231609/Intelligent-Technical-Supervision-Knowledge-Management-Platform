import { ConfigProvider, theme } from "antd";
import zhCN from "antd/locale/zh_CN";

import AppRouter from "@/router";
import "@/styles/global.css";

const App = () => {
  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          borderRadius: 6,
          colorPrimary: "#0ea5cf",
          fontFamily:
            "Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Microsoft YaHei, sans-serif"
        }
      }}
    >
      <AppRouter />
    </ConfigProvider>
  );
};

export default App;
