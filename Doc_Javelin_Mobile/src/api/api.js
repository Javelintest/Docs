import axios from "axios";
import { Platform } from "react-native";

// UPDATE THIS IP ADDRESS TO YOUR COMPUTER'S LOCAL IP IF TESTING ON PHYSICAL DEVICE
// For Android Emulator, 10.0.2.2 points to localhost of the host machine.
// For iOS Simulator, localhost is localhost.
const API_BASE_URL = Platform.select({
  android: "http://10.0.2.2:8000",
  ios: "http://localhost:8000",
  default: "http://192.168.5.36:8000", // Replace with your computer's IP
});

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const getApiUrl = () => API_BASE_URL;

export default api;
