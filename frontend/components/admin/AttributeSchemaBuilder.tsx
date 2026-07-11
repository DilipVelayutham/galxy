// components/admin/AttributeSchemaBuilder.tsx
'use client';
import { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { NeonButton } from '@/components/ui/NeonButton';
import { NeonInput } from '@/components/ui/NeonInput';
import { Toast } from '@/components/ui/Toast';
import { SchemaWarningModal } from '@/components/admin/SchemaWarningModal';
import { AttributeSchemaItem, AttributeType } from '@/types/category';
import { updateCategory } from '@/lib/api/categories';

type Props = {
  categoryId: string;
  schema: AttributeSchemaItem[];
  onSchemaChange: (newSchema: AttributeSchemaItem[]) => void;
};

export const AttributeSchemaBuilder = ({ categoryId, schema, onSchemaChange }: Props) => {
  const [showWarning, setShowWarning] = useState(false);
  const [pendingDeleteIdx, setPendingDeleteIdx] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const persist = async (newSchema: AttributeSchemaItem[]) => {
    try {
      await updateCategory(categoryId, { attribute_schema: newSchema });
      onSchemaChange(newSchema);
      setToast('Attribute schema saved');
    } catch {
      setToast('Failed to save attribute schema');
    }
  };

  const handleAdd = () => {
    const newItem: AttributeSchemaItem = {
      key: '',
      label: '',
      type: 'text_input',
      affects_ai_preview: false,
      required: false,
      display_order: schema.length,
    };
    const newSchema = [...schema, newItem];
    persist(newSchema);
  };

  const handleDelete = (idx: number) => {
    setPendingDeleteIdx(idx);
    setShowWarning(true);
  };

  const confirmDelete = async () => {
    if (pendingDeleteIdx === null) return;
    const newSchema = schema.filter((_item, i) => i !== pendingDeleteIdx);
    await persist(newSchema);
    setShowWarning(false);
    setPendingDeleteIdx(null);
  };

  const cancelDelete = () => {
    setShowWarning(false);
    setPendingDeleteIdx(null);
  };

  const handleChange = <K extends keyof AttributeSchemaItem>(
    idx: number,
    field: K,
    value: AttributeSchemaItem[K]
  ) => {
    const newSchema = schema.map((item, i) => (i === idx ? { ...item, [field]: value } : item));
    // optimistic UI update; persist after change
    persist(newSchema);
  };

  const onDragEnd = async (result: DropResult) => {
    if (!result.destination) return;
    const reordered = Array.from(schema);
    const [removed] = reordered.splice(result.source.index, 1);
    reordered.splice(result.destination.index, 0, removed);
    // update display_order based on new position
    reordered.forEach((item, i) => {
      item.display_order = i;
    });
    await persist(reordered);
  };

  return (
    <section className="mt-8">
      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
      <h3 className="text-xl font-semibold mb-4 text-primaryNeon">Attribute Schema</h3>
      <NeonButton variant="primary" onClick={handleAdd} className="mb-4">
        Add Attribute
      </NeonButton>

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="attr-schema">
          {provided => (
            <div ref={provided.innerRef} {...provided.droppableProps} className="space-y-3">
              {schema.map((attr, idx) => (
                <Draggable key={idx} draggableId={`attr-${idx}`} index={idx}>
                  {provided => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className="p-4 bg-panelCharcoal rounded shadow-neon flex items-center gap-4"
                    >
                      <div {...provided.dragHandleProps} className="cursor-move text-textMuted">
                        ☰
                      </div>
                      <div className="flex-1 grid grid-cols-2 gap-2">
                        <NeonInput
                          placeholder="Key"
                          value={attr.key}
                          onChange={e => handleChange(idx, 'key', e.target.value)}
                        />
                        <NeonInput
                          placeholder="Label"
                          value={attr.label}
                          onChange={e => handleChange(idx, 'label', e.target.value)}
                        />
                        <select
                          value={attr.type}
                          onChange={e => handleChange(idx, 'type', e.target.value as AttributeType)}
                          className="rounded bg-panelCharcoal text-textPrimary p-1"
                        >
                          {[
                            'select',
                            'color_swatch',
                            'image_swatch',
                            'toggle',
                            'slider',
                            'text_input',
                            'number',
                          ].map(t => (
                            <option key={t} value={t}>
                              {t}
                            </option>
                          ))}
                        </select>
                        <label className="flex items-center space-x-1">
                          <input
                            type="checkbox"
                            checked={attr.required}
                            onChange={e => handleChange(idx, 'required', e.target.checked)}
                          />
                          <span className="text-sm">Required</span>
                        </label>
                        <label className="flex items-center space-x-1">
                          <input
                            type="checkbox"
                            checked={attr.affects_ai_preview}
                            onChange={e => handleChange(idx, 'affects_ai_preview', e.target.checked)}
                          />
                          <span className="text-sm">Affects AI Preview</span>
                        </label>
                      </div>
                      <NeonButton variant="danger" onClick={() => handleDelete(idx)}>
                        Delete
                      </NeonButton>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <SchemaWarningModal
        isOpen={showWarning}
        onConfirm={confirmDelete}
        onCancel={cancelDelete}
      />
    </section>
  );
};
