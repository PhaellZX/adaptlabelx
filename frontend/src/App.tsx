import { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [message, setMessage] = useState('');

  // O 'useEffect' executa a função uma vez, quando o componente é montado
  useEffect(() => {
    // Pega a URL da variável de ambiente que criamos no arquivo .env
    const backendUrl = import.meta.env.VITE_API_URL;

    // Faz a requisição para o backend usando a URL correta
    fetch(`${backendUrl}/`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Erro de rede: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => setMessage(data.message))
      .catch(error => {
        console.error('Falha ao conectar com a API do backend:', error);
        setMessage('Erro ao conectar com a API.');
      });
  }, []); // O array vazio '[]' garante que a requisição só aconteça uma vez

  return (
    <>
      <div>
        <h1>Adaptação da API</h1>
      </div>
      <div className="card">
        <p>
          A mensagem do seu backend é: <br />
          <strong>{message || 'Carregando...'}</strong>
        </p>
      </div>
    </>
  );
}

export default App;