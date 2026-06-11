import React, { useRef, useState } from 'react';
import Button from '../common/Button.tsx';

interface CanvasProps {
  onRecognize: (blob: Blob) => void;
  loading: boolean;
}

export default function Canvas({ onRecognize, loading }: CanvasProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  // Drawing handlers placeholder
  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      ctx?.clearRect(0, 0, canvas.width, canvas.height);
    }
  };

  const submitCanvas = () => {
    canvasRef.current?.toBlob((blob) => {
      if (blob) onRecognize(blob);
    }, 'image/png');
  };

  return (
    <div className="canvas-wrapper">
      <canvas 
        ref={canvasRef} 
        width={600} 
        height={400} 
        style={{ border: '2px solid #ccc', borderRadius: '8px', background: '#fff' }}
      />
      <div className="controls">
        <Button onClick={clearCanvas}>Clear</Button>
        <Button onClick={submitCanvas} disabled={loading}>
          {loading ? 'Recognizing...' : 'Recognize'}
        </Button>
      </div>
    </div>
  );
}
