-- Insert a post's card mark (front matter `image:` under images/marks/posts/)
-- into the post body, after the first top-level paragraph.
-- Skipped when the post already places a .post-mark image itself, or when
-- `image:` is a real figure (not a mark), or when `post-mark: false` is set.

local function already_placed(blocks)
  local found = false
  blocks:walk({
    Image = function(img)
      if img.classes:includes("post-mark") then found = true end
    end
  })
  return found
end

function Pandoc(doc)
  local meta = doc.meta
  if meta["post-mark"] == false then return doc end
  if not meta.image then return doc end
  local src = pandoc.utils.stringify(meta.image)
  if not src:match("images/marks/posts/") then return doc end
  if already_placed(doc.blocks) then return doc end

  local img = pandoc.Image({}, src, "", pandoc.Attr("", { "post-mark" }, { { "alt", "" } }))
  for i, block in ipairs(doc.blocks) do
    if block.t == "Para" then
      doc.blocks:insert(i + 1, pandoc.Para({ img }))
      return doc
    end
  end
  return doc
end
