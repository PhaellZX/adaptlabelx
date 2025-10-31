import { Container } from 'react-bootstrap';

export function Footer() {
  // 'mt-auto' (margin-top: auto) é a magia do Bootstrap
  // que funciona com o nosso 'app-wrapper' flex para empurrar o rodapé para baixo.
  return (
    <footer className="mt-auto py-3 bg-dark text-light">
      <Container className="text-center">
        <small>AdaptLabelX &copy; 2025. Criado por Raphael Tavares.</small>
      </Container>
    </footer>
  );
}