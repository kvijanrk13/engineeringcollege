import React from 'react';

export interface QuillyLogoProps {
  className?: string;
  height?: number | string;
  width?: number | string;
}

export function QuillyLogo({ className, height = 16, width = 16 }: QuillyLogoProps) {
  return (
    <svg
      aria-hidden
      className={className}
      fill="none"
      height={height}
      viewBox="0 0 16 16"
      width={width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M10.5 1V2L8.5 3H10.5V4L8.60254 5H13L14.5 6.5V13.5L13 15H3L1.5 13.5V6.5L3 5H7.5L5.5 4V3H7.5L5.5 2V1L7.5 0H8.5L10.5 1ZM6 8.5C5.17157 8.5 4.5 9.17157 4.5 10C4.5 10.8284 5.17157 11.5 6 11.5C6.82843 11.5 7.5 10.8284 7.5 10C7.5 9.17157 6.82843 8.5 6 8.5ZM10 8.5C9.17157 8.5 8.5 9.17157 8.5 10C8.5 10.8284 9.17157 11.5 10 11.5C10.8284 11.5 11.5 10.8284 11.5 10C11.5 9.17157 10.8284 8.5 10 8.5Z"
        fill="#161F19"
      />
    </svg>
  );
}
