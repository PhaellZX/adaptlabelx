// frontend/src/components/CreateDatasetModal/index.tsx

import { useState, useEffect } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import api from '../../services/api';

// Interface para as props do componente
interface CreateDatasetModalProps {
  show: boolean;
  handleClose: () => void;
  onDatasetCreated: (newDataset: any) => void;
}

export function CreateDatasetModal({ show, handleClose, onDatasetCreated }: CreateDatasetModalProps) {
  // States para os campos do formulário
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [annotationType, setAnnotationType] = useState('detection');
  
  // States para o filtro de classes
  const [availableClasses, setAvailableClasses] = useState<Record<string, string>>({});
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  const [loadingClasses, setLoadingClasses] = useState(true);

  // Efeito para buscar as classes disponíveis quando o modal é aberto
  useEffect(() => {
    if (show) {
      setLoadingClasses(true);
      api.get('/models/available-classes')
        .then(response => {
          // A resposta é um objeto {0: 'person', 1: 'bicycle', ...}
          setAvailableClasses(response.data);
        })
        .catch(err => console.error("Falha ao buscar classes", err))
        .finally(() => setLoadingClasses(false));
    }
  }, [show]); // Roda toda vez que 'show' muda para true

  // Função para lidar com o clique em um checkbox de classe
  const handleClassToggle = (className: string) => {
    setSelectedClasses(prev => 
      prev.includes(className)
        ? prev.filter(c => c !== className) // Remove a classe se já estiver selecionada
        : [...prev, className] // Adiciona a classe
    );
  };

  // Função para limpar todos os estados e fechar o modal
  const handleModalClose = () => {
    setName('');
    setDescription('');
    setAnnotationType('detection');
    setSelectedClasses([]);
    setAvailableClasses({});
    handleClose();
  }

  // Função para enviar o formulário
  const handleSubmit = async () => {
    try {
      await api.post('/datasets/', { 
        name, 
        description, 
        annotation_type: annotationType,
        selected_classes: selectedClasses // Envia a lista de classes selecionadas
      });
      onDatasetCreated(true); // Notifica o pai (podemos apenas passar true para recarregar)
      handleModalClose(); // Limpa e fecha o modal
    } catch (error) {
      console.error("Falha ao criar dataset:", error);
      alert("Erro ao criar dataset. Tente novamente.");
    }
  };

  // Converte o objeto de classes {0: 'person', ...} em um array de nomes ['person', ...] e ordena
  const classNames = Object.values(availableClasses).sort();

  return (
    <Modal show={show} onHide={handleModalClose}>
      <Modal.Header closeButton>
        <Modal.Title>Criar Novo Dataset</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group className="mb-3">
            <Form.Label>Nome do Dataset</Form.Label>
            <Form.Control
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Imagens de Gatos"
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Descrição (Opcional)</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Tipo de Anotação</Form.Label>
            <Form.Select value={annotationType} onChange={e => setAnnotationType(e.target.value)}>
              <option value="detection">Detecção (Caixas)</option>
              <option value="segmentation">Segmentação (YOLO-Seg)</option>
              <option value="sam">Segmentação (SAM - Alta Qualidade)</option>
            </Form.Select>
          </Form.Group>
          
          {/* Novo Bloco: Seletor de Classes */}
          <Form.Group className="mb-3">
            <Form.Label>Filtrar Classes (Opcional)</Form.Label>
            <Form.Text className="d-block mb-2">
              Selecione apenas as classes que você deseja anotar. Se nada for selecionado, todas as classes serão usadas.
            </Form.Text>
            <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #dee2e6', padding: '10px', borderRadius: '5px' }}>
              {loadingClasses ? (
                <p className="text-center">Carregando classes...</p>
              ) : (
                classNames.map(className => (
                  <Form.Check 
                    key={className}
                    type="checkbox"
                    id={`class-${className}`}
                    label={className}
                    checked={selectedClasses.includes(className)}
                    onChange={() => handleClassToggle(className)}
                  />
                ))
              )}
            </div>
          </Form.Group>

        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleModalClose}>
          Cancelar
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Salvar
        </Button>
      </Modal.Footer>
    </Modal>
  );
}