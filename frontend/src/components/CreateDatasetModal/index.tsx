// frontend/src/components/CreateDatasetModal/index.tsx

import { useState } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import api from '../../services/api';

interface CreateDatasetModalProps {
  show: boolean;
  handleClose: () => void;
  onDatasetCreated: (newDataset: any) => void;
}

export function CreateDatasetModal({ show, handleClose, onDatasetCreated }: CreateDatasetModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [annotationType, setAnnotationType] = useState('detection'); // Estado para o tipo

  const handleSubmit = async () => {
    try {
      // Envia o novo tipo de anotação para o backend
      const response = await api.post('/datasets/', { 
        name, 
        description, 
        annotation_type: annotationType 
      });
      onDatasetCreated(response.data); // Informa o componente pai sobre o novo dataset
      handleClose(); // Fecha o modal
      
      // Limpa os campos para a próxima vez
      setName('');
      setDescription('');
      setAnnotationType('detection');
    } catch (error) {
      console.error("Falha ao criar dataset:", error);
      alert("Erro ao criar dataset. Tente novamente.");
    }
  };

  const handleModalClose = () => {
      // Limpa os campos ao fechar sem salvar
      setName('');
      setDescription('');
      setAnnotationType('detection');
      handleClose();
  }

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
          
          {/* Campo de seleção para o tipo de anotação */}
          <Form.Group className="mb-3">
            <Form.Label>Tipo de Anotação</Form.Label>
            <Form.Select value={annotationType} onChange={e => setAnnotationType(e.target.value)}>
              <option value="detection">Detecção (Caixas)</option>
              <option value="segmentation">Segmentação (Polígonos)</option>
            </Form.Select>
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