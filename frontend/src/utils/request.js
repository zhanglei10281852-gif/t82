import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import { message } from "ant-design-vue";

const request = axios.create({
  baseURL: "/api",
  timeout: 15000,
});

request.interceptors.request.use(
  (config) => {
    const auth = useAuthStore();
    if (auth.token) {
      config.headers.Authorization = `Bearer ${auth.token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore();
      auth.logout();
      window.location.href = "/login";
    }
    const msg = error.response?.data?.detail || error.message || "请求失败";
    message.error(msg);
    return Promise.reject(error);
  },
);

export default request;
