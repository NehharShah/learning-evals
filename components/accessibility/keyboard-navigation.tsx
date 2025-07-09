"use client"

import { useEffect } from "react"

export function KeyboardNavigation() {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Global keyboard shortcuts
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case "k":
            event.preventDefault()
            // Focus search input
            const searchInput = document.querySelector("[data-search-input]") as HTMLInputElement
            if (searchInput) {
              searchInput.focus()
            }
            break
          case "u":
            event.preventDefault()
            // Focus upload area
            const uploadArea = document.querySelector("[data-upload-area]") as HTMLElement
            if (uploadArea) {
              uploadArea.focus()
            }
            break
          case "p":
            event.preventDefault()
            // Focus playground
            const playground = document.querySelector("[data-playground-input]") as HTMLTextAreaElement
            if (playground) {
              playground.focus()
            }
            break
        }
      }

      // Escape key to close modals/dropdowns
      if (event.key === "Escape") {
        const openDialog = document.querySelector('[data-state="open"]')
        if (openDialog) {
          const closeButton = openDialog.querySelector("[data-dialog-close]") as HTMLButtonElement
          if (closeButton) {
            closeButton.click()
          }
        }
      }
    }

    document.addEventListener("keydown", handleKeyDown)
    return () => document.removeEventListener("keydown", handleKeyDown)
  }, [])

  return null
}
