# -*- coding: utf-8 -*-
"""
luna_lib.py — Astronomía y gráficos de fases lunares
San Juan, Argentina (Lat -31.5373°, Lon -68.5257°, 650 m s.n.m., UTC-3)
Lo usan app_gradio.py y app_streamlit.py
"""
import math
from datetime import datetime, timedelta, timezone

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

try:
    from zoneinfo import ZoneInfo
    TZ = ZoneInfo("America/Argentina/San_Juan")
except Exception:
    TZ = timezone(timedelta(hours=-3), "UTC-3")

LAT, LON, ALT = -31.5373, -68.5257, 650
SYN = 29.530588853
DIAS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]

# ---------------- Astronomía (Meeus, baja precisión) ----------------
def a_jd(dt_utc):
    y, m = dt_utc.year, dt_utc.month
    d = dt_utc.day + (dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)/24
    if m <= 2:
        y, m = y-1, m+12
    a = y//100
    b = 2 - a + a//4
    return math.floor(365.25*(y+4716)) + math.floor(30.6001*(m+1)) + d + b - 1524.5

def _T(jd): return (jd - 2451545.0)/36525.0

def sol_longitud(T):
    L0 = 280.46646 + 36000.76983*T + 0.0003032*T*T
    M = math.radians((357.52911 + 35999.05029*T - 0.0001537*T*T) % 360)
    C = ((1.914602-0.004817*T-0.000014*T*T)*math.sin(M)
         + (0.019993-0.000101*T)*math.sin(2*M) + 0.000289*math.sin(3*M))
    return (L0 + C) % 360

def _elem_luna(T):
    D  = math.radians((297.8501921 + 445267.1114034*T - 0.0018819*T**2 + T**3/545868 - T**4/113065000) % 360)
    M  = math.radians((357.5291092 + 35999.0502909*T - 0.0001536*T**2 + T**3/24490000) % 360)
    Mp = math.radians((134.9633964 + 477198.8675055*T + 0.0087414*T**2 + T**3/69699 - T**4/14712000) % 360)
    F  = math.radians((93.2720950 + 483202.0175233*T - 0.0036539*T**2 - T**3/3526000 + T**4/863310000) % 360)
    return D, M, Mp, F

def luna_longitud(T):
    D, M, Mp, F = _elem_luna(T)
    L = 218.3164477 + 481267.88123421*T - 0.0015786*T**2 + T**3/538841 - T**4/65194000
    l = (6.288774*math.sin(Mp) + 1.274027*math.sin(2*D-Mp) + 0.658314*math.sin(2*D)
         + 0.213618*math.sin(2*Mp) - 0.185116*math.sin(M) - 0.114332*math.sin(2*F)
         + 0.058793*math.sin(2*D-2*Mp) + 0.057066*math.sin(2*D-M-Mp)
         + 0.053322*math.sin(2*D+Mp) + 0.045758*math.sin(2*D-M) - 0.040923*math.sin(M-Mp))
    return (L + l) % 360

def luna_latitud(T):
    D, M, Mp, F = _elem_luna(T)
    return (5.128189*math.sin(F) + 0.280606*math.sin(Mp+F) + 0.277693*math.sin(Mp-F)
            + 0.173238*math.sin(2*D-F) + 0.055413*math.sin(2*D-Mp+F)
            + 0.046272*math.sin(2*D-Mp-F) + 0.032573*math.sin(2*D+F) + 0.017198*math.sin(2*Mp+F))

def luna_distancia(T):
    D, M, Mp, F = _elem_luna(T)
    return (385000.56 - 20905.355*math.cos(Mp) - 3699.111*math.cos(2*D-Mp)
            - 2955.968*math.cos(2*D) - 569.925*math.cos(2*Mp))

def luna_radec(T):
    lam = math.radians(luna_longitud(T)); bet = math.radians(luna_latitud(T))
    eps = math.radians(23.43929111 - 0.0130042*T)
    ra = math.degrees(math.atan2(math.sin(lam)*math.cos(eps) - math.tan(bet)*math.sin(eps),
                                 math.cos(lam))) % 360
    dec = math.degrees(math.asin(math.sin(bet)*math.cos(eps)
                                 + math.cos(bet)*math.sin(eps)*math.sin(lam)))
    return ra, dec

def lst_grados(jd):
    return (280.46061837 + 360.98564736629*(jd - 2451545.0) + LON) % 360

def altura_luna(dt_utc):
    jd = a_jd(dt_utc)
    ra, dec = luna_radec(_T(jd))
    H = math.radians(lst_grados(jd) - ra)
    la, ld = math.radians(LAT), math.radians(dec)
    return math.degrees(math.asin(math.sin(la)*math.sin(ld)
                                  + math.cos(la)*math.cos(ld)*math.cos(H)))

def info_fase(dt_utc):
    T = _T(a_jd(dt_utc))
    el = (luna_longitud(T) - sol_longitud(T)) % 360
    p = el/360
    return p, el, (1-math.cos(math.radians(el)))/2, p*SYN, luna_distancia(T)

FASES = [(0.0339, "Luna Nueva (Novilunio)", "🌑"), (0.2161, "Creciente", "🌒"),
         (0.2839, "Cuarto Creciente", "🌓"), (0.4661, "Gibosa Creciente", "🌔"),
         (0.5339, "Luna Llena (Plenilunio)", "🌕"), (0.7161, "Gibosa Menguante", "🌖"),
         (0.7839, "Cuarto Menguante", "🌗"), (0.9661, "Menguante (Balsámica)", "🌘"),
         (1.0001, "Luna Nueva (Novilunio)", "🌑")]

def nombre_fase(p):
    for lim, nom, emo in FASES:
        if p < lim:
            return nom, emo
    return FASES[-1][1], FASES[-1][2]

def elongacion(dt):
    T = _T(a_jd(dt))
    return (luna_longitud(T) - sol_longitud(T)) % 360

def _firmado(dt, obj):
    return ((elongacion(dt) - obj + 180) % 360) - 180

def proxima_fase(dt_utc, obj):
    t = dt_utc
    s_prev = _firmado(t, obj)
    paso = timedelta(hours=1)
    for _ in range(24*31):
        t2 = t + paso
        s = _firmado(t2, obj)
        if s_prev < 0 <= s:
            a, b = t, t2
            for _ in range(35):
                m = a + (b-a)/2
                if _firmado(m, obj) < 0:
                    a = m
                else:
                    b = m
            return b
        s_prev, t = s, t2
    return None

def salida_puesta(fecha_local):
    h0 = 0.125
    ini = datetime(fecha_local.year, fecha_local.month, fecha_local.day, 0, 0, tzinfo=TZ)
    paso = timedelta(minutes=3)
    def alt(t): return altura_luna(t.astimezone(timezone.utc)) - h0
    def refinar(a, b):
        for _ in range(25):
            m = a + (b-a)/2
            if (alt(m) > 0) == (alt(a) > 0):
                a = m
            else:
                b = m
        return b
    pa, pt = alt(ini), ini
    sal = pue = None
    ma, mt = pa, pt
    for i in range(1, 481):
        t = ini + paso*i
        a = alt(t)
        if a > ma:
            ma, mt = a, t
        if pa < 0 <= a and sal is None:
            sal = refinar(pt, t)
        elif pa >= 0 > a and pue is None:
            pue = refinar(pt, t)
        pa, pt = a, t
    return sal, pue, (mt if ma > -5 else None)

def fmt_hora(dt):
    return "--:--" if dt is None else dt.astimezone(TZ).strftime("%H:%M")

def fmt_completo(dt):
    l = dt.astimezone(TZ)
    return f"{DIAS[l.weekday()]} {l.day:02d}/{l.month:02d}/{l.year} {l.hour:02d}:{l.minute:02d}"

# ---------------- Gráficos ----------------
def disco(ax, p, sur=True):
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.add_patch(plt.Circle((0, 0), 1.0, color='#222228', zorder=1))
    m = math.cos(2*math.pi*p)
    creciente = p < 0.5
    ys = np.linspace(-1, 1, 300)
    chord = np.sqrt(np.clip(1-ys**2, 0, 1))
    xs = np.concatenate([chord, (m*chord)[::-1]])
    yy = np.concatenate([ys, ys[::-1]])
    if ((0 if creciente else 1) + (1 if sur else 0)) % 2 == 1:
        xs = -xs
    ax.fill(xs, yy, color='#f4e9c7', zorder=2)
    ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, ec='#8899bb', lw=1.2, zorder=3))

def render_fig(local, sur=True):
    utc = local.astimezone(timezone.utc)
    p, el, ilum, edad, dist = info_fase(utc)
    nom, emo = nombre_fase(p)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.6))
    fig.patch.set_facecolor('#0d1420')
    for ax in (ax1, ax2):
        ax.set_facecolor('#0d1420')

    disco(ax1, p, sur)
    ax1.set_title(f"{emo} {nom}\n{ilum*100:.1f}% iluminada · edad {edad:.2f} días",
                  color='#f4e9c7', fontsize=11)

    base = local.replace(hour=0, minute=0, second=0, microsecond=0)
    hs = np.arange(0, 24.0001, 0.1)
    alts = np.array([altura_luna((base + timedelta(hours=float(h))).astimezone(timezone.utc))
                     for h in hs])
    ax2.plot(hs, alts, color='#9fd0a8', lw=2)
    ax2.axhline(0, color='#66788f', lw=0.8)
    ax2.fill_between(hs, 0, alts, where=alts > 0, color='#9fd0a8', alpha=0.25)
    ax2.set_xlim(0, 24)
    ax2.set_ylim(-90, 90)
    ax2.set_xlabel("hora local", color='#cfe0f4')
    ax2.set_ylabel("altitud (°)", color='#cfe0f4')
    ax2.set_title("Altura de la Luna durante el día", color='#f4e9c7', fontsize=11)
    ax2.tick_params(colors='#cfe0f4')
    for sp in ax2.spines.values():
        sp.set_color('#33456b')
    fig.tight_layout()
    return fig

def resumen_md(local):
    utc = local.astimezone(timezone.utc)
    p, el, ilum, edad, dist = info_fase(utc)
    nom, emo = nombre_fase(p)
    sal, pue, tr = salida_puesta(local)
    lineas = [
        f"**Fecha y hora local:** {fmt_completo(local)}",
        f"**Fase:** {emo} {nom}",
        f"**Iluminación:** {ilum*100:.1f} %   ·   **Elongación:** {el:.1f}°",
        f"**Edad lunar:** {edad:.2f} días   ·   **Distancia:** {dist:,.0f} km",
        f"**Salida:** {fmt_hora(sal)}   ·   **Tránsito:** {fmt_hora(tr)}   ·   **Puesta:** {fmt_hora(pue)}",
        "",
        "**Próximas fases principales (hora de San Juan):**",
    ]
    objs = [(0, "🌑 Luna Nueva"), (90, "🌓 Cuarto Creciente"),
            (180, "🌕 Luna Llena"), (270, "🌗 Cuarto Menguante")]
    eventos = sorted((t, n) for o, n in objs if (t := proxima_fase(utc, o)) is not None)
    for t, n in eventos:
        lineas.append(f"- {n}: {fmt_completo(t)}")
    return "\n".join(lineas)