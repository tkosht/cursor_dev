// public/elements/Counter.jsx
import { Button } from "@/components/ui/button";
import { Plus, X } from "lucide-react";

export default function Counter() {
  return (
    <div id="custom-counter" className="mt-2 flex items-center gap-3">
      <span>Count: {props.count}</span>
      <Button id="increment" onClick={() => updateElement({ ...props, count: (props.count ?? 0) + 1 })}>
        <Plus className="w-4 h-4" /> Increment
      </Button>
      <Button id="remove" variant="outline" onClick={deleteElement}>
        <X className="w-4 h-4" /> Remove
      </Button>
    </div>
  );
}
