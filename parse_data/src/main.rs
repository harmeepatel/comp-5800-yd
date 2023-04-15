#![allow(dead_code, unused)]

use itertools::{EitherOrBoth::*, Itertools};
use kdam::{tqdm, BarExt};
use serde_json::Value;

const SPECIAL_CHARS: [char; 36] = [
    '!', '"', '#', '$', '%', '&', '\'', '‘', '’', '(', ')', '*', '+', ',', '-', '—', '–', '.', '/',
    ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~',
];

struct Config {
    jsonl_path: String,
    source: String,
    target: String,
}
impl Config {
    fn build(args: &mut Vec<String>) -> Result<Self, &'static str> {
        Ok(Config {
            jsonl_path: match args.get(1) {
                Some(q) => q.to_owned(),
                None => return Err("Provide a path to jsonl file."),
            },
            source: match args.get(2) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save source file."),
            },
            target: match args.get(3) {
                Some(fp) => fp.to_owned(),
                None => return Err("Provide a path to save target file."),
            },
        })
    }
}

fn main() {
    let config =
        Config::build(&mut std::env::args().collect::<Vec<String>>()).unwrap_or_else(|e| {
            eprintln!("{}", e);
            std::process::exit(1);
        });
    let file_content = std::fs::read_to_string(&config.jsonl_path).unwrap_or_else(|e| {
        eprintln!("{}", e);
        std::process::exit(1);
    });

    let mut json_lines: Vec<Value> = Vec::with_capacity(file_content.len());
    for line in file_content.lines() {
        json_lines.push(serde_json::from_str(line).unwrap_or_else(|e| {
            eprintln!("Something went wrong converting to json with error:\n{}", e);
            std::process::exit(1);
        }));
    }

    let data = parse_text(&json_lines).unwrap_or_else(|e| {
        eprintln!("Someting went wrong parsing text with err:\n{}", e);
        std::process::exit(1);
    });

    println!("__src_len__: {}", data.0.len());
    println!("__tgt_len__: {}", data.1.len());
    if let Err(e) = save_files(&config, data) {
        eprintln!("err: {}", e);
        std::process::exit(1);
    }
}

fn save_files(config: &Config, (src, tgt): (Vec<String>, Vec<String>)) -> Result<(), String> {
    let _ = save_file(&config.source, src)?;
    let _ = save_file(&config.target, tgt)?;

    Ok(())
}

fn save_file(path: &str, data: Vec<String>) -> Result<(), String> {
    let data = data.join("\n");
    let path = match std::env::current_dir() {
        Ok(cur_dir) => {
            let tp = cur_dir.join(path);
            tp.to_str()
                .unwrap_or_else(|| {
                    eprintln!("Problem converting PathBuf to str");
                    std::process::exit(1);
                })
                .to_owned()
        }
        Err(e) => return Err(format!("Problem reading current dir with error:\n{}", e)),
    };

    match std::fs::write(&path, data) {
        Ok(_) => {
            println!("Written to {}", path);
        }
        Err(e) => {
            return Err(format!(
                "Problem writing to source file: {}, with error:\n{}",
                path, e
            ))
        }
    };
    Ok(())
}
// remove special chars and lower-casing line
fn filter_line(val: &Value) -> String {
    val.as_str()
        .unwrap_or_else(|| {
            eprintln!("Something went wrong parsing to string.");
            std::process::exit(1);
        })
        .replace(&SPECIAL_CHARS, " ")
        .trim()
        .to_lowercase()
        .split(' ')
        .collect::<Vec<_>>()
        .iter()
        .filter_map(|word| match word.is_empty() {
            true => None,
            false => Some(*word),
        })
        .collect::<Vec<_>>()
        .join(" ")
}

fn parse_text(json_vec: &Vec<Value>) -> Result<(Vec<String>, Vec<String>), String> {
    let mut removed: Vec<String> = Vec::new();
    let mut source_lines: Vec<String> = Vec::new();
    let mut target_lines: Vec<String> = Vec::new();

    let mut source_text: String;
    let mut target_text: String;
    let mut edits: &Vec<Value>;
    let mut last_edit: &Value;

    let mut prev = (String::new(), String::new());
    let mut flag = false;
    let mut pb1 = tqdm!(
        total = json_vec.len(),
        desc = "parsing objects",
        position = 0,
        force_refresh = true
    );

    'objects: for object in json_vec.iter() {
        pb1.update(1);

        edits = object["edits"].as_array().unwrap_or_else(|| {
            eprintln!("Something went wrong parsing to array.");
            std::process::exit(1);
        });
        last_edit = &edits[edits.len() - 1];

        if !last_edit["is_typo"].as_bool().unwrap_or(false)
            || last_edit["src"]["lang"].as_str().unwrap_or("") != "eng"
        {
            continue;
        }

        source_text = filter_line(&last_edit["src"]["text"]);
        target_text = filter_line(&last_edit["tgt"]["text"]);

        if flag {
            if source_text.eq(&prev.0) || target_text.eq(&prev.1) {
                prev.0 = source_text.clone();
                prev.1 = target_text.clone();
                continue 'objects;
            }
        }
        prev.0 = source_text.clone();
        prev.1 = target_text.clone();
        flag = true;

        if source_text.eq(&target_text) {
            continue;
        }

        'filter0x: for pair in source_text.split(' ').zip_longest(target_text.split(' ')) {
            match pair {
                Both(sw, tw) => {
                    for c in sw.chars() {
                        if (!c.is_ascii_alphanumeric() && !c.is_whitespace()) {
                            removed.push(format!("__src_na__: {}", &source_text));
                            removed.push(format!("__tgt_na__: {}", &target_text));
                            continue 'objects;
                        }
                    }
                    for c in tw.chars() {
                        if (!c.is_ascii_alphanumeric() && !c.is_whitespace()) {
                            removed.push(format!("__src_na__: {}", &source_text));
                            removed.push(format!("__tgt_na__: {}", &target_text));
                            continue 'objects;
                        }
                    }
                    if sw.starts_with("0x") || tw.starts_with("0x") {
                        removed.push(format!("__src__: {}", &source_text));
                        removed.push(format!("__tgt__: {}", &target_text));
                        continue 'objects;
                    }
                }
                Left(sw) => {
                    for c in sw.chars() {
                        if (!c.is_ascii_alphanumeric() && !c.is_whitespace()) {
                            removed.push(format!("__src_na__: {}", &source_text));
                            continue 'objects;
                        }
                    }
                    if sw.starts_with("0x") {
                        removed.push(format!("__src__: {}", &source_text));
                        continue 'objects;
                    }
                }
                Right(tw) => {
                    for c in tw.chars() {
                        if (!c.is_ascii_alphanumeric() && !c.is_whitespace()) {
                            removed.push(format!("__tgt_na__: {}", &target_text));
                            continue 'objects;
                        }
                    }
                    if tw.starts_with("0x") {
                        removed.push(format!("__tgt__: {}", &target_text));
                        continue 'objects;
                    }
                }
            }
        }

        source_lines.push(source_text);
        target_lines.push(target_text);
    }

    let _ = save_file("../data/removed.txt", removed)?;

    Ok((source_lines, target_lines))
}
