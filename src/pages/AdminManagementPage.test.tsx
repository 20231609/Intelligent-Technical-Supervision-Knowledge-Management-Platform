import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import AdminManagementPage from "./AdminManagementPage";

describe("AdminManagementPage", () => {
  it("renders management sections required by the specification", () => {
    render(
      <MemoryRouter initialEntries={["/admin/settings"]}>
        <AdminManagementPage />
      </MemoryRouter>
    );

    expect(screen.getAllByText("大模型配置").length).toBeGreaterThan(0);
    expect(screen.getByText("嵌入模型")).toBeInTheDocument();
    expect(screen.getByText("重排序模型")).toBeInTheDocument();
    expect(screen.getByText("知识问答")).toBeInTheDocument();
    expect(screen.getByText("检索体验测试")).toBeInTheDocument();
    expect(screen.getByLabelText("术语知识库")).toBeInTheDocument();
    expect(screen.getByLabelText("技术监督知识库")).toBeInTheDocument();
    expect(screen.getByLabelText("Top K")).toBeInTheDocument();
  });
});
