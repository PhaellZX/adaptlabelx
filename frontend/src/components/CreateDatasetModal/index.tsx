// frontend/src/components/CreateDatasetModal/index.tsx

import { useState, useEffect } from 'react';
import { Modal, Button, Form, Spinner } from 'react-bootstrap';
import api from '../../services/api';

// Interface para as props do componente
interface CreateDatasetModalProps {
  show: boolean;
  handleClose: () => void;
  onDatasetCreated: (success: boolean) => void;
}

// --- 1. Nova interface para o Modelo Customizado ---
interface CustomModel {
  id: number;
  name: string;
  model_type: string;
}

export function CreateDatasetModal({ show, handleClose, onDatasetCreated }: CreateDatasetModalProps) {
  // States para o formulário
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  
  // --- 2. States para os modelos e classes ---
  const [availableClasses, setAvailableClasses] = useState<Record<string, string>>({});
  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  const [customModels, setCustomModels] = useState<CustomModel[]>([]);
  const [selectedModel, setSelectedModel] = useState('default-sam'); // Valor padrão
  
  const [loading, setLoading] = useState(true);

  // Efeito para buscar classes E modelos customizados
  useEffect(() => {
    if (show) {
      setLoading(true);
      // Busca as 80 classes padrão
      const fetchClasses = api.get('/models/available-classes');
      // Busca os modelos .pt do usuário
      const fetchCustomModels = api.get('/custom-models/');

      // Roda as duas requisições em paralelo
      Promise.all([fetchClasses, fetchCustomModels])
        .then(([classesResponse, modelsResponse]) => {
          setAvailableClasses(classesResponse.data);
          setCustomModels(modelsResponse.data);
        })
        .catch(err => console.error("Falha ao buscar dados para o modal", err))
        .finally(() => setLoading(false));
    }
  }, [show]);

  // Handler para o checkbox de classe
  const handleClassToggle = (className: string) => {
    setSelectedClasses(prev => 
      prev.includes(className) ? prev.filter(c => c !== className) : [...prev, className]
    );
  };

  // Handler para limpar e fechar o modal
  const handleModalClose = () => {
    setName('');
    setDescription('');
    setSelectedClasses([]);
    setSelectedModel('default-sam'); // Reseta para o padrão
    handleClose();
  }

  // --- 3. Lógica principal de Submit ---
  const handleSubmit = async () => {
    let annotation_type = '';
    let custom_model_id: number | null = null;

    // Processa a seleção do modelo
    if (selectedModel.startsWith('default-')) {
      // É um modelo padrão (ex: "default-sam")
      annotation_type = selectedModel.replace('default-', ''); // "sam"
    } else {
      // É um modelo customizado (ex: "custom-5")
      custom_model_id = parseInt(selectedModel.replace('custom-', ''));
      // Encontra o tipo do modelo (detection/segmentation)
      const model = customModels.find(m => m.id === custom_model_id);
      annotation_type = model ? model.model_type : 'detection';
    }

    try {
      await api.post('/datasets/', { 
        name, 
        description, 
        annotation_type: annotation_type,
        selected_classes: selectedClasses.length > 0 ? selectedClasses : null,
        custom_model_id: custom_model_id
      });
      onDatasetCreated(true);
      handleModalClose();
    } catch (error) {
      console.error("Falha ao criar dataset:", error);
      alert("Erro ao criar dataset. Tente novamente.");
    }
  };

  const classNames = Object.values(availableClasses).sort();

  return (
    <Modal show={show} onHide={handleModalClose}>
      <Modal.Header closeButton>
        <Modal.Title>Criar Novo Dataset</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {loading ? (
          <div className="text-center">
            <Spinner animation="border" />
            <p>Carregando dados...</p>
          </div>
        ) : (
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Nome do Dataset</Form.Label>
              <Form.Control type="text" value={name} onChange={(e) => setName(e.target.value)} />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Descrição (Opcional)</Form.Label>
              <Form.Control as="textarea" rows={3} value={description} onChange={(e) => setDescription(e.target.value)} />
            </Form.Group>
            
            {/* --- 4. O Novo Seletor de Modelo --- */}
            <Form.Group className="mb-3">
              <Form.Label>Modelo de Anotação</Form.Label>
              <Form.Select value={selectedModel} onChange={e => setSelectedModel(e.target.value)}>
                <optgroup label="Modelos Padrão">
                  <option value="default-sam">Segmentação (SAM - Alta Qualidade)</option>
                  <option value="default-segmentation">Segmentação (YOLO-Seg)</option>
                  <option value="default-detection">Detecção (Caixas)</option>
                </optgroup>
                
                {customModels.length > 0 && (
                  <optgroup label="Meus Modelos">
                    {customModels.map(model => (
                      <option key={model.id} value={`custom-${model.id}`}>
                        {model.name} ({model.model_type})
                      </option>
                    ))}
                  </optgroup>
                )}
              </Form.Select>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Filtrar Classes (Opcional)</Form.Label>
              <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #dee2e6', padding: '10px', borderRadius: '5px' }}>
                {classNames.map(className => (
                  <Form.Check 
                    key={className}
                    type="checkbox"
                    label={className}
                    checked={selectedClasses.includes(className)}
                    onChange={() => handleClassToggle(className)}
                  />
                ))}
              </div>
            </Form.Group>
          </Form>
        )}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleModalClose}>Cancelar</Button>
        <Button variant="primary" onClick={handleSubmit} disabled={loading}>Salvar</Button>
      </Modal.Footer>
    </Modal>
  );
}