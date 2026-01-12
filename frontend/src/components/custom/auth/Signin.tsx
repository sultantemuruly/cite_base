import { useState } from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { useNavigate } from "react-router";

const formSchema = z.object({
  email: z.string().email("Enter a valid email").max(100),
  password: z
    .string()
    .min(6, "Password must be at least 6 characters.")
    .max(100),
});

type FormValues = z.infer<typeof formSchema>;

function Signin() {
  const [loading, setLoading] = useState(false);

  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const navigate = useNavigate();

  const onSubmit = async (values: FormValues) => {
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/auth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: values.email,
          password: values.password,
        }),
      });

      if (!response.ok) {
        setLoading(false);
        throw new Error("Failed to sign in");
      }

      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      navigate("/dashboard");
    } catch (error) {
      setLoading(false);
      console.error("Signin error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="you@example.com"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Password</FormLabel>
                <FormControl>
                  <Input type="password" placeholder="••••••••" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button disabled={loading} className="w-full" type="submit">
            {loading ? "Signing in..." : "Sign In"}
          </Button>

          <p className="text-center">
            New here?{" "}
            <a href="/auth/signup" className="text-blue-500">
              Create an account
            </a>
          </p>
        </form>
      </Form>
    </div>
  );
}

export default Signin;
