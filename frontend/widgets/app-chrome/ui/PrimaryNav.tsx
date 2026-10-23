"use client";

import { useTranslations } from "next-intl";
import {
  useEffect,
  useId,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { Link, usePathname } from "@/i18n/navigation";
import type { NavZone, NavZoneId } from "@/lib/navZones";

function pathActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

function zoneActive(pathname: string, zone: NavZone): boolean {
  return zone.items.some((item) => pathActive(pathname, item.href));
}

type PrimaryNavProps = {
  zones: NavZone[];
};

export function PrimaryNav({ zones }: PrimaryNavProps) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  const [openId, setOpenId] = useState<NavZoneId | null>(null);
  const rootRef = useRef<HTMLElement>(null);
  const baseId = useId();

  // useEffectEvent is not always available in the Next/Webpack React runtime.
  const close = () => setOpenId(null);

  useEffect(() => {
    setOpenId(null);
  }, [pathname]);

  useEffect(() => {
    if (openId == null) return;
    const onPointer = (e: MouseEvent | PointerEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpenId(null);
    };
    const onKey = (e: globalThis.KeyboardEvent) => {
      if (e.key === "Escape") setOpenId(null);
    };
    document.addEventListener("pointerdown", onPointer);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointer);
      document.removeEventListener("keydown", onKey);
    };
  }, [openId]);

  const onTriggerKeyDown = (
    e: KeyboardEvent<HTMLButtonElement>,
    zoneId: NavZoneId,
    index: number,
  ) => {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      const next = zones[(index + 1) % zones.length];
      setOpenId(next.id);
      document.getElementById(`${baseId}-trigger-${next.id}`)?.focus();
    } else if (e.key === "ArrowLeft") {
      e.preventDefault();
      const prev = zones[(index - 1 + zones.length) % zones.length];
      setOpenId(prev.id);
      document.getElementById(`${baseId}-trigger-${prev.id}`)?.focus();
    } else if (e.key === "ArrowDown" || e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      setOpenId(zoneId);
      requestAnimationFrame(() => {
        document
          .querySelector<HTMLElement>(`#${baseId}-menu-${zoneId} a`)
          ?.focus();
      });
    } else if (e.key === "Escape") {
      close();
    }
  };

  return (
    <nav
      ref={rootRef}
      className="primary-nav"
      aria-label={t("primaryNav")}
    >
      <ul>
        {zones.map((zone, index) => {
          const open = openId === zone.id;
          const active = zoneActive(pathname, zone);
          const menuId = `${baseId}-menu-${zone.id}`;
          const triggerId = `${baseId}-trigger-${zone.id}`;
          const alignEnd = index >= zones.length - 2;
          return (
            <li key={zone.id} className="relative">
              <button
                id={triggerId}
                type="button"
                className={`primary-nav__trigger ${
                  active ? "primary-nav__trigger--active" : ""
                } ${open ? "primary-nav__trigger--open" : ""}`}
                aria-expanded={open}
                aria-haspopup="menu"
                aria-controls={menuId}
                onClick={() => setOpenId(open ? null : zone.id)}
                onKeyDown={(e) => onTriggerKeyDown(e, zone.id, index)}
              >
                <span>{t(zone.labelKey)}</span>
                <span
                  className={`primary-nav__chevron ${open ? "primary-nav__chevron--open" : ""}`}
                  aria-hidden
                >
                  ▾
                </span>
              </button>
              {open ? (
                <ul
                  id={menuId}
                  role="menu"
                  aria-labelledby={triggerId}
                  className={`primary-nav__menu${alignEnd ? " primary-nav__menu--end" : ""}`}
                >
                  {zone.items.map((item) => {
                    const itemActive = pathActive(pathname, item.href);
                    const descKey = `${item.key}Desc` as `${typeof item.key}Desc`;
                    return (
                      <li key={item.href} role="none">
                        <Link
                          role="menuitem"
                          href={item.href}
                          className={`primary-nav__item ${
                            itemActive ? "primary-nav__item--active" : ""
                          }`}
                          aria-current={itemActive ? "page" : undefined}
                          onClick={() => close()}
                        >
                          <span className="primary-nav__item-label">
                            {t(item.key)}
                          </span>
                          <span className="primary-nav__item-sep" aria-hidden>
                            —
                          </span>
                          <span className="primary-nav__item-desc">
                            {t(descKey)}
                          </span>
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
