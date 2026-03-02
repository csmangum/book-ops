"use client";

import Editor from "@monaco-editor/react";

type ManuscriptEditorProps = {
  value: string;
  readOnly?: boolean;
};

export function ManuscriptEditor({ value, readOnly = true }: ManuscriptEditorProps) {
  return (
    <div className="overflow-hidden rounded-md border">
      <Editor
        height="70vh"
        defaultLanguage="markdown"
        value={value}
        options={{
          minimap: { enabled: false },
          readOnly,
          fontSize: 13,
          wordWrap: "on",
        }}
      />
    </div>
  );
}
