// frontend/src/components/CreateDatasetModal/index.tsx

import { useState, useEffect } from 'react';
import { Modal, Button, Form, Alert } from 'react-bootstrap';
import api from '../../services/api';
import { Dataset } from '../../types';

// O tipo para os modelos que vêm do backend
// (Já estava no seu ficheiro)
interface ModelOption {
  id: string | number;
  name: string;
}

// Os IDs dos modelos que devem mostrar o seletor de classes
// (Já estava no seu ficheiro)
const STANDARD_MODELS = ["yolov8n_det", "yolov8n_seg", "sam"];

// Os 3 modelos padrão que sempre aparecem
const standardModelsList: ModelOption[] = [
  { id: "yolov8n_det", name: "YOLOv8n (Detecção)" },
  { id: "yolov8n_seg", name: "YOLOv8n (Segmentação)" },
  { id: "sam", name: "Segment Anything (SAM)" }
];

// As 80 classes do COCO (Já estava no seu ficheiro)
const COCO_CLASSES = [
  "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat", "traffic light",
  "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog", "horse", "sheep", "cow",
  "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
  "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard",
  "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
  "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
  "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse", "remote", "keyboard",
  "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase",
  "scissors", "teddy bear", "hair drier", "toothbrush"
];

interface CreateDatasetModalProps {
  show: boolean;
  handleClose: () => void;
  onDatasetCreated: (newDataset: Dataset) => void;
}

export function CreateDatasetModal({ show, handleClose, onDatasetCreated }: CreateDatasetModalProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  
  // --- ESTADO PARA OS MODELOS ---
  const [selectedModel, setSelectedModel] = useState<string>("yolov8n_det");
  const [customModels, setCustomModels] = useState<ModelOption[]>([]);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  // --- FIM DO ESTADO ---

  const [selectedClasses, setSelectedClasses] = useState<string[]>([]);
  
  // Lógica para mostrar/esconder o seletor de classes (O seu ficheiro já tinha)
  const isStandardModel = STANDARD_MODELS.includes(selectedModel);

  // --- BUSCAR MODELOS CUSTOMIZADOS QUANDO O MODAL ABRE ---
  useEffect(() => {
    if (show) {
      // Limpa o formulário ao abrir
      setName('');
      setDescription('');
      setSelectedModel('yolov8n_det');
      setSelectedClasses([]);
      setErrorMessage('');
      
      // Busca os modelos customizados
      const fetchCustomModels = async () => {
        setIsLoadingModels(true);
        try {
          const response = await api.get('/custom-models');
          // Mapeia os dados da API (que vêm do schema CustomModel)
          // para o tipo ModelOption
          const fetchedModels: ModelOption[] = response.data.map((model: any) => ({
            id: model.id.toString(), // O 'value' do <option> deve ser string
            name: `(Custom) ${model.name}` // Adiciona um prefixo para clareza
          }));
          setCustomModels(fetchedModels);
        } catch (error) {
          console.error("Falha ao buscar modelos customizados:", error);
          setErrorMessage("Não foi possível carregar seus modelos customizados.");
        } finally {
          setIsLoadingModels(false);
        }
      };
      
      fetchCustomModels();
    }
  }, [show]); // Depende apenas de 'show'
  // --- FIM DO CÓDIGO DE BUSCA ---

  const handleClassChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const options = e.target.options;
    const values: string[] = [];
    for (let i = 0, l = options.length; i < l; i++) {
      if (options[i].selected) {
        values.push(options[i].value);
      }
    }
    setSelectedClasses(values);
  };

  const handleSubmit = async (e: React.FormEvent | React.MouseEvent) => {
    e.preventDefault();
    setErrorMessage('');
    
    if (!name) {
      setErrorMessage('O nome do dataset é obrigatório.');
      return;
    }
    
    const payload = {
      name: name,
      description: description,
      model_id: selectedModel,
      classes_to_annotate: isStandardModel ? selectedClasses : null
    };

    try {
      const response = await api.post('/datasets/', payload);
      onDatasetCreated(response.data); // Envia o novo dataset de volta para o Dashboard
      handleClose(); // Fecha o modal
    } catch (error: any) {
      console.error('Falha ao criar dataset:', error);
      if (error.response && error.response.data && error.response.data.detail) {
        setErrorMessage(error.response.data.detail);
      } else {
        setErrorMessage('Ocorreu um erro. Tente novamente.');
      }
    }
  };

  // Combina as listas de modelos
  // const allModels = [...standardModelsList, ...customModels];

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Criar Novo Dataset</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {errorMessage && <Alert variant="danger">{errorMessage}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Nome do Dataset *</Form.Label>
            <Form.Control
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Treino de Cães e Gatos"
              required
            />
          </Form.Group>
          <Form.Group className="mb-3">
            <Form.Label>Descrição</Form.Label>
            <Form.Control
              as="textarea"
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: Imagens da webcam para detectar gatos."
            />
          </Form.Group>
          
          <Form.Group className="mb-3">
            <Form.Label>Modelo de Anotação</Form.Label>
            <Form.Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={isLoadingModels}
            >
              {/* --- DROPDOWN DINÂMICO --- */}
              <option value="" disabled>
                {isLoadingModels ? "Carregando modelos..." : "Selecione um modelo"}
              </option>
              
              {/* Grupo de Modelos Padrão */}
              <optgroup label="Modelos Padrão">
                {standardModelsList.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </optgroup>

              {/* Grupo de Modelos Customizados (só aparece se houver algum) */}
              {customModels.length > 0 && (
                <optgroup label="Meus Modelos Customizados">
                  {customModels.map(model => (
                    <option key={model.id} value={model.id}>
                      {model.name}
                    </option>
                  ))}
                </optgroup>
              )}
              {/* --- FIM DO DROPDOWN DINÂMICO --- */}
            </Form.Select>
          </Form.Group>
          
          {/* --- DROPDOWN DE CLASSES (CONDICIONAL) --- */}
          {/* (Esta lógica sua já estava perfeita) */}
          {isStandardModel && (
            <Form.Group className="mb-3">
              <Form.Label>Classes a Anotar</Form.Label>
              <Form.Text className="d-block mb-2">
                Segure Ctrl (ou Cmd ⌘) para selecionar várias.
              </Form.Text>
              <Form.Select
                multiple
                value={selectedClasses}
                onChange={handleClassChange}
                style={{ height: '150px' }}
              >
                {COCO_CLASSES.map(cls => (
                  <option key={cls} value={cls}>
                    {cls}
                  </option>
                ))}\
              </Form.Select>
            </Form.Group>
          )}
          
          <Form.Control type="submit" className="d-none" />
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose}>
          Cancelar
        </Button>
        <Button variant="primary" onClick={handleSubmit} disabled={!name}>
          Criar
        </Button>
      </Modal.Footer>
    </Modal>
  );
}