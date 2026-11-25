import { redirect } from 'next/navigation';

// The old 1:1 chat lives on as the talk pod.
export default function Page() {
  redirect('/talk');
}
