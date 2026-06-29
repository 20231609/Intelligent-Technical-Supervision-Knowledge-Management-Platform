let loginPromise: Promise<string> | null = null;

export async function ensureAuthToken(): Promise<string> {
  const existing = localStorage.getItem("auth_token");
  if (existing) {
    return existing;
  }

  if (!loginPromise) {
    loginPromise = fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: "admin", password: "123456" })
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("自动登录失败");
        }
        return response.json();
      })
      .then((payload) => {
        const token = payload.token || payload.access_token;
        if (!token) {
          throw new Error("登录响应缺少 token");
        }
        localStorage.setItem("auth_token", token);
        return token;
      })
      .finally(() => {
        loginPromise = null;
      });
  }

  return loginPromise;
}
