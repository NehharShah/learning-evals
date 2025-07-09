// Mock implementation for react-dropzone since it's not available in Next.js
export const useDropzone = ({ onDrop, accept, multiple }: any) => {
  const getRootProps = () => ({
    onClick: () => {
      const input = document.createElement("input")
      input.type = "file"
      input.multiple = multiple
      input.accept = Object.keys(accept).join(",")
      input.onchange = (e: any) => {
        const files = Array.from(e.target.files)
        onDrop(files)
      }
      input.click()
    },
  })

  const getInputProps = () => ({
    style: { display: "none" },
  })

  return {
    getRootProps,
    getInputProps,
    isDragActive: false,
  }
}
