import { Header } from './header';
import { Footer } from './footer';
import { QueryProvider } from '../providers/query-provider';
import { Toaster } from '@/components/ui/sonner';

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <QueryProvider>
      <div className="min-h-screen flex flex-col bg-white">
        <Header />
        
        <main className="flex-1">
          {children}
        </main>
        
        <Footer />
        
        {/* Toast notifications */}
        <Toaster 
          position="bottom-right"
          expand={true}
          richColors
          closeButton
        />
      </div>
    </QueryProvider>
  );
}