import { Outlet } from 'react-router-dom';
import { AppNavbar } from '../components/AppNavbar';
import { Footer } from '../components/Footer';

export function ProtectedLayout() {
  return (
    // Este é o layout 'app-wrapper' que está no App.css
    <div className="app-wrapper">
      <AppNavbar />
      
      {/* Este é o 'main-content' que está no App.css */}
      <main className="main-content">
        {/* O Outlet renderiza a rota filha (Dashboard, Models, etc.) */}
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}