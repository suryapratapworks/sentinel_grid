import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';
import { LoginView } from './components/LoginView';
import { DashboardView } from './pages/DashboardView';
import { GISMapView } from './pages/GISMapView';
import { CameraRegistryView } from './pages/CameraRegistryView';
import { LiveMatrixView } from './pages/LiveMatrixView';
import { VehicleInvestigatorView } from './pages/VehicleInvestigatorView';
import { WatchlistsView } from './pages/WatchlistsView';
import { AlertCenterView } from './pages/AlertCenterView';
import { FederationHubView } from './pages/FederationHubView';
import { EvidenceVaultView } from './pages/EvidenceVaultView';
import { api } from './services/api';
import { DashboardStats, Camera, Alert, Adapter, Watchlist, EvidenceItem, VehicleRoute, AuthUser } from './types';

export const App: React.FC = () => {
  const [currentUser, setCurrentUser] = useState<AuthUser | null>(() => {
    const savedUser = localStorage.getItem('sentinel_user');
    const token = localStorage.getItem('sentinel_token');
    if (savedUser && token) {
      try {
        return JSON.parse(savedUser);
      } catch (_) {
        return null;
      }
    }
    return null;
  });

  const [activeView, setActiveView] = useState<string>('dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [adapters, setAdapters] = useState<Adapter[]>([]);
  const [watchlists, setWatchlists] = useState<Watchlist[]>([]);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [selectedRouteForMap, setSelectedRouteForMap] = useState<VehicleRoute | null>(null);

  const [isDark, setIsDark] = useState<boolean>(() => {
    const saved = localStorage.getItem('sentinel-theme');
    return saved ? saved === 'dark' : true;
  });

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.remove('light');
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
      root.classList.add('light');
    }
    localStorage.setItem('sentinel-theme', isDark ? 'dark' : 'light');
  }, [isDark]);

  const loadData = async () => {
    if (!currentUser) return;
    try {
      const [statsData, camerasData, alertsData, adaptersData, watchlistsData, evidenceData] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getCameras().catch(() => []),
        api.getAlerts().catch(() => []),
        api.getAdapters().catch(() => []),
        api.getWatchlists().catch(() => []),
        api.getEvidence().catch(() => []),
      ]);
      setStats(statsData);
      setCameras(camerasData);
      setAlerts(alertsData);
      setAdapters(adaptersData);
      setWatchlists(watchlistsData);
      setEvidence(evidenceData);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (currentUser) {
      loadData();
      const interval = setInterval(loadData, 10000);
      return () => clearInterval(interval);
    }
  }, [currentUser]);

  const handleLogout = () => {
    localStorage.removeItem('sentinel_token');
    localStorage.removeItem('sentinel_user');
    setCurrentUser(null);
  };

  const handleShowOnMap = (route: VehicleRoute) => {
    setSelectedRouteForMap(route);
    setActiveView('gis');
  };

  const handleInvestigatePlate = (_plate: string) => {
    setActiveView('investigator');
  };

  // If user is not authenticated, render Login Screen
  if (!currentUser) {
    return <LoginView onLoginSuccess={(user) => setCurrentUser(user)} />;
  }

  return (
    <div className="min-h-screen bg-base text-primary flex flex-col transition-colors duration-300">
      <Navbar
        stats={stats}
        activeView={activeView}
        onRefresh={loadData}
        onSelectView={setActiveView}
        isDark={isDark}
        onToggleTheme={() => setIsDark(prev => !prev)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar
          activeView={activeView}
          onSelectView={setActiveView}
          alertCount={stats?.active_alerts ?? 0}
        />

        <main className="flex-1 p-6 overflow-y-auto max-h-[calc(100vh-4rem)]">
          {activeView === 'dashboard' && (
            <DashboardView
              stats={stats}
              cameras={cameras}
              alerts={alerts}
              adapters={adapters}
              onSelectView={setActiveView}
              onRefresh={loadData}
            />
          )}
          {activeView === 'gis' && (
            <GISMapView
              cameras={cameras}
              highlightRoute={selectedRouteForMap}
            />
          )}
          {activeView === 'matrix' && (
            <LiveMatrixView
              cameras={cameras}
              onRefresh={loadData}
            />
          )}
          {activeView === 'registry' && (
            <CameraRegistryView
              cameras={cameras}
              currentUser={currentUser}
              onRefresh={loadData}
              onSelectCamera={() => setActiveView('gis')}
            />
          )}
          {activeView === 'investigator' && (
            <VehicleInvestigatorView
              onShowOnMap={handleShowOnMap}
            />
          )}
          {activeView === 'watchlists' && (
            <WatchlistsView
              watchlists={watchlists}
              onRefresh={loadData}
            />
          )}
          {activeView === 'alerts' && (
            <AlertCenterView
              alerts={alerts}
              onRefresh={loadData}
              onInvestigatePlate={handleInvestigatePlate}
            />
          )}
          {activeView === 'federation' && (
            <FederationHubView
              adapters={adapters}
              onRefresh={loadData}
            />
          )}
          {activeView === 'evidence' && (
            <EvidenceVaultView
              evidence={evidence}
              onRefresh={loadData}
            />
          )}
        </main>
      </div>
    </div>
  );
};