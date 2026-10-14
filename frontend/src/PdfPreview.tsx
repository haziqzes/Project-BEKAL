import { useEffect, useRef, useState } from 'react'
import { getDocument, GlobalWorkerOptions, type PDFDocumentProxy, type RenderTask } from 'pdfjs-dist'
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

GlobalWorkerOptions.workerSrc = workerUrl

export function PdfPreview({ url }: { url: string }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [document, setDocument] = useState<PDFDocumentProxy | null>(null)
  const [pageNumber, setPageNumber] = useState(1)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    const task = getDocument({ url })
    setDocument(null)
    setPageNumber(1)
    setError('')
    void task.promise.then((loaded) => {
      if (cancelled) {
        void task.destroy()
      } else {
        setDocument(loaded)
      }
    }).catch(() => {
      if (!cancelled) setError('Could not display the original PDF. It may be missing; receipt details remain available.')
    })
    return () => {
      cancelled = true
      void task.destroy()
    }
  }, [url])

  useEffect(() => {
    if (!document || !canvasRef.current) return
    let cancelled = false
    let renderTask: RenderTask | undefined
    setError('')
    void document.getPage(pageNumber).then((page) => {
      if (cancelled) return
      const canvas = canvasRef.current
      if (!canvas) return
      const viewport = page.getViewport({ scale: 1.5 })
      canvas.width = viewport.width
      canvas.height = viewport.height
      const canvasContext = canvas.getContext('2d')
      if (!canvasContext) throw new Error('Canvas is unavailable')
      renderTask = page.render({ canvas, canvasContext, viewport })
      return renderTask.promise
    }).catch(() => {
      if (!cancelled) setError('Could not render this PDF page.')
    })
    return () => {
      cancelled = true
      renderTask?.cancel()
    }
  }, [document, pageNumber])

  return (
    <div className="pdf-preview" aria-label="Original receipt PDF preview">
      {!document && !error && <p>Loading PDF preview…</p>}
      {error && <p role="alert" className="error">{error}</p>}
      {document && (
        <>
          <div className="page-controls">
            <button type="button" className="secondary" disabled={pageNumber === 1} onClick={() => setPageNumber((page) => page - 1)}>Previous page</button>
            <span>Page {pageNumber} of {document.numPages}</span>
            <button type="button" className="secondary" disabled={pageNumber === document.numPages} onClick={() => setPageNumber((page) => page + 1)}>Next page</button>
          </div>
          <canvas ref={canvasRef} aria-label={`Receipt PDF page ${pageNumber}`} />
        </>
      )}
    </div>
  )
}
