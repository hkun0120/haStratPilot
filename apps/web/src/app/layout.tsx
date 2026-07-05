import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StratPilot | 策略驾驶舱",
  description: "港美股策略回测、回撤分析与风控工作台",
  icons: {
    icon: "/icon.svg"
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
