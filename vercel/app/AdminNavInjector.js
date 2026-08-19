"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

export default function AdminNavInjector() {
  const pathname = usePathname();

  useEffect(() => {
    const ensureAdminTab = () => {
      const nav = document.querySelector(".main-nav");
      if (!nav) return;

      let button = nav.querySelector('[data-admin-nav="true"]');
      if (!button) {
        button = document.createElement("button");
        button.type = "button";
        button.textContent = "管理者用";
        button.dataset.adminNav = "true";
        button.addEventListener("click", () => {
          window.location.href = "/admin";
        });
        nav.appendChild(button);
      }

      button.classList.toggle("active", pathname.startsWith("/admin"));
    };

    ensureAdminTab();
    const observer = new MutationObserver(ensureAdminTab);
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [pathname]);

  return null;
}
