import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { NewRunModal } from '../components/NewRunModal';

export function NewRunPage() {
  const navigate = useNavigate();

  useEffect(() => {
    const html = document.documentElement;
    const body = document.body;
    const root = document.getElementById('root');

    const previousHtmlOverflow = html.style.overflow;
    const previousBodyOverflow = body.style.overflow;
    const previousRootOverflow = root?.style.overflow ?? '';
    const previousRootHeight = root?.style.height ?? '';

    html.style.overflow = 'auto';
    body.style.overflow = 'auto';
    if (root) {
      root.style.overflow = 'visible';
      root.style.height = 'auto';
    }

    return () => {
      html.style.overflow = previousHtmlOverflow;
      body.style.overflow = previousBodyOverflow;
      if (root) {
        root.style.overflow = previousRootOverflow;
        root.style.height = previousRootHeight;
      }
    };
  }, []);

  return <NewRunModal pageMode onClose={() => navigate('/')} />;
}
