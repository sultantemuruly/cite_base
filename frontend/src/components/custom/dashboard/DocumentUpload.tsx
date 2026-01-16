import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormDescription,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useRef, useCallback } from "react";

const documentSchema = z.object({
  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be less than 200 characters"),
  document: z
    .instanceof(FileList)
    .refine((files) => files?.length === 1, "Please select a file")
    .refine(
      (files) => files?.[0]?.size <= 10 * 1024 * 1024,
      "File size must be less than 10MB",
    )
    .refine((files) => {
      const file = files?.[0];
      const allowedTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
      ];
      return allowedTypes.includes(file?.type || "");
    }, "File type must be PDF, DOC, DOCX, or TXT"),
});

type DocumentFormValues = z.infer<typeof documentSchema>;

interface DocumentUploadProps {
  onUploadSuccess?: () => void;
}

const DocumentUpload = ({ onUploadSuccess }: DocumentUploadProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const form = useForm<DocumentFormValues>({
    resolver: zodResolver(documentSchema),
  });

  const onSubmit = useCallback(
    async (values: DocumentFormValues) => {
      try {
        const file = values.document[0];
        const formData = new FormData();
        formData.append("file", file);
        formData.append("title", values.title);

        const token = localStorage.getItem("token");
        const headers: HeadersInit = token
          ? { Authorization: `Bearer ${token}` }
          : {};

        const response = await fetch("http://localhost:8000/documents/upload", {
          method: "POST",
          headers,
          body: formData,
        });

        const data = await response.json();

        if (response.ok) {
          console.log("Document uploaded successfully:", data);
          form.reset();
          if (fileInputRef.current) {
            fileInputRef.current.value = "";
          }
          // You can add a toast notification here for better UX
          alert(`Successfully uploaded ${data.chunk_count} document chunk(s)`);
          if (onUploadSuccess) {
            onUploadSuccess();
          }
        } else {
          form.setError("document", {
            message: data.message || "Failed to upload document",
          });
        }
      } catch (error) {
        console.error("Upload error:", error);
        form.setError("document", {
          message: "An error occurred during upload",
        });
      }
    },
    [form, fileInputRef, onUploadSuccess],
  );

  const handleSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      form.handleSubmit(onSubmit)(e);
    },
    [form, onSubmit],
  );

  return (
    <Form {...form}>
      <form onSubmit={handleSubmit} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Document Title</FormLabel>
              <FormControl>
                <Input placeholder="Enter document title..." {...field} />
              </FormControl>
              <FormDescription>
                Give your document a descriptive title
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="document"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Upload Document</FormLabel>
              <FormControl>
                <Input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={(e) => {
                    field.onChange(e.target.files);
                  }}
                />
              </FormControl>
              <FormDescription>
                Upload a PDF, DOC, DOCX, or TXT file (max 10MB)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Uploading..." : "Upload Document"}
        </Button>
      </form>
    </Form>
  );
};
export { DocumentUpload };
