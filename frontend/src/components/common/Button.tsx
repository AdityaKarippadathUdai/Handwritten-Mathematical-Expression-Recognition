import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export default function Button({ children, ...props }: ButtonProps) {
  return (
    <button 
      style={{ padding: '8px 16px', margin: '4px', cursor: 'pointer' }}
      {...props}
    >
      {children}
    </button>
  );
}
