"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface DropdownContextType {
  openDropdownId: string | null;
  toggleDropdown: (id: string) => void;
  closeDropdown: () => void;
}

const DropdownContext = createContext<DropdownContextType | undefined>(undefined);

export function DropdownProvider({ children }: { children: ReactNode }) {
  const [openDropdownId, setOpenDropdownId] = useState<string | null>(null);

  const toggleDropdown = (id: string) => {
    setOpenDropdownId(prev => prev === id ? null : id);
  };

  const closeDropdown = () => {
    setOpenDropdownId(null);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      
      // Don't close if clicking on a dropdown trigger or menu
      if (target.closest('[data-dropdown-id]') || 
          target.closest('[role="menu"]') ||
          target.closest('[aria-haspopup="menu"]')) {
        return;
      }
      
      closeDropdown();
    };

    if (openDropdownId) {
      document.addEventListener("click", handleClickOutside);
      return () => document.removeEventListener("click", handleClickOutside);
    }
  }, [openDropdownId]);

  return (
    <DropdownContext.Provider value={{ openDropdownId, toggleDropdown, closeDropdown }}>
      {children}
    </DropdownContext.Provider>
  );
}

export function useDropdown() {
  const context = useContext(DropdownContext);
  if (!context) {
    throw new Error("useDropdown must be used within DropdownProvider");
  }
  return context;
}

// Hook up dropdown behavior to scraped Asana elements
export function DropdownManager({ children }: { children: ReactNode }) {
  const { toggleDropdown } = useDropdown();

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      
      // Find if clicked element is a button or has button role
      const button = target.closest('[role="button"]') as HTMLElement ||
                     target.closest('button') as HTMLElement ||
                     target.closest('[data-testid*="Dropdown"]') as HTMLElement ||
                     target.closest('[aria-haspopup="menu"]') as HTMLElement ||
                     target.closest('.Clickable') as HTMLElement;
      
      if (button) {
        // Generate unique ID for this dropdown
        const dropdownId = button.getAttribute('data-dropdown-id') || 
                          button.getAttribute('data-testid') || 
                          button.id || 
                          `dropdown-${Math.random().toString(36).substr(2, 9)}`;
        
        // Store the ID on the element for future reference
        if (!button.getAttribute('data-dropdown-id')) {
          button.setAttribute('data-dropdown-id', dropdownId);
        }
        
        // Toggle the dropdown
        toggleDropdown(dropdownId);
        
        // Update aria-expanded attribute
        const isExpanded = button.getAttribute('aria-expanded') === 'true';
        button.setAttribute('aria-expanded', (!isExpanded).toString());
        
        e.preventDefault();
        e.stopPropagation();
      }
    };

    document.addEventListener('click', handleClick, true);
    return () => document.removeEventListener('click', handleClick, true);
  }, [toggleDropdown]);

  return <>{children}</>;
}
