import { AuthProvider } from '@/contexts/AuthContext';
import Navbar from '@/components/Navbar';
import '@/styles/globals.css';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Navbar />
          <main className="container">{children}</main>
        </AuthProvider>
      </body>
    </html>
  );
}