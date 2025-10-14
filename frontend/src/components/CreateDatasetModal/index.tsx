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

  const handleSubmit = async () => {
    try {
      const response = await api.post('/datasets/', { name, description });
      onDatasetCreated(response.data); // Informa o componente pai sobre o novo dataset
      handleClose(); // Fecha o modal
    } catch (error) {
      console.error("Falha ao criar dataset:", error);
      alert("Erro ao criar dataset. Tente novamente.");
    }
  };

  return (
    <Modal show={show} onHide={handleClose}>
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
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancelar
        </Button>
        <Button variant="primary" onClick={handleSubmit}>
          Salvar
        </Button>
      </Modal.Footer>
    </Modal>
  );
}