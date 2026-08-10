import { useTheme } from '@quillbot/styleq';
import React from 'react';
import styled from 'styled-components';

interface ToolbarQuillyProps {
  disabled?: boolean;
  height?: string;
  hoverColor?: string;
  width?: string;
}

const StyledSvg = styled.svg<{ $hoverColor?: string }>`
  &:hover {
    path {
      fill: ${(props) => props.$hoverColor};
    }
  }
  transition: all 0.2s ease-in-out;
  position: relative;
  top: -0.5px;
`;

function ToolbarQuilly({
  disabled,
  height = '13px',
  hoverColor,
  width = '11px',
}: ToolbarQuillyProps) {
  const theme = useTheme();

  const color = disabled ? theme.palette.icon.inverse.bold : theme.palette.icon.default;

  return (
    <StyledSvg
      $hoverColor={hoverColor}
      fill={color}
      height={height}
      preserveAspectRatio="xMidYMid meet"
      viewBox="0 0 11 13"
      width={width}
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M9.80041 3.94065H5.79964L7.45106 3.125V2.24057H5.79964L7.45106 1.62146V1.21855L5.79964 0H5.18036L3.53876 1.21855V1.63129L5.18036 2.25039H3.53876V3.16431L5.18036 3.94065H1.17959L0 5.08058V11.3306L1.17959 12.5H9.80041L10.98 11.3306V5.08058L9.80041 3.94065ZM3.82383 9.4831C3.13574 9.4831 2.55577 8.92296 2.55577 8.21541C2.55577 7.50786 3.13574 6.94772 3.82383 6.94772C4.51192 6.94772 5.09189 7.50786 5.09189 8.21541C5.09189 8.92296 4.53158 9.4831 3.82383 9.4831ZM7.14634 9.4831C6.45825 9.4831 5.87828 8.92296 5.87828 8.21541C5.87828 7.50786 6.45825 6.94772 7.14634 6.94772C7.83443 6.94772 8.4144 7.50786 8.4144 8.21541C8.4144 8.92296 7.85409 9.4831 7.14634 9.4831Z"
        fill={color}
      />
    </StyledSvg>
  );
}

export default ToolbarQuilly;
