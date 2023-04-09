#![allow(dead_code, unused)]

use itertools::{EitherOrBoth::*, Itertools};
use kdam::{tqdm, BarExt};
use serde_json::Value;

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
    let src = src.join("\n");
    let tgt = tgt.join("\n");

    let (s_path, t_path) = match std::env::current_dir() {
        Ok(cur_dir) => {
            let source_cur_dir = cur_dir.join(&config.source);
            let target_cur_dir = cur_dir.join(&config.target);
            (
                source_cur_dir
                    .to_str()
                    .unwrap_or_else(|| {
                        eprintln!("Problem converting PathBuf to str");
                        std::process::exit(1);
                    })
                    .to_owned(),
                target_cur_dir
                    .to_str()
                    .unwrap_or_else(|| {
                        eprintln!("Problem converting PathBuf to str");
                        std::process::exit(1);
                    })
                    .to_owned(),
            )
        }
        Err(e) => return Err(format!("Problem reading current dir with error:\n{}", e)),
    };

    match std::fs::write(&s_path, src) {
        Ok(_) => {
            println!("Written to {}", &s_path);
        }
        Err(e) => {
            return Err(format!(
                "Problem writing to source file: {}, with error:\n{}",
                &s_path, e
            ))
        }
    };
    match std::fs::write(&t_path, tgt) {
        Ok(_) => {
            println!("Written to {}", &s_path);
        }
        Err(e) => {
            return Err(format!(
                "Problem writing to target file: {}, with error:\n{}",
                &t_path, e
            ))
        }
    };

    Ok(())
}

fn parse_text(json_vec: &Vec<Value>) -> Result<(Vec<String>, Vec<String>), String> {
    let special_chars = [
        "!", "\"", "#", "$", "%", "&", "'", "(", ")", "*", "+", ",", "-", ".", "/", ":", ";", "<",
        "=", ">", "?", "@", "[", "\\", "]", "^", "_", "`", "{", "|", "}", "~",
    ];

    let mut removed: Vec<String> = Vec::new();
    let mut source_lines: Vec<String> = Vec::new();
    let mut target_lines: Vec<String> = Vec::new();
    let mut pb1 = tqdm!(
        total = json_vec.len(),
        desc = "parsing objects",
        position = 0,
        force_refresh = true
    );

    'objects: for object in json_vec.iter() {
        pb1.update(1);
        let edits = object["edits"].as_array().unwrap_or_else(|| {
            eprintln!("Something went wrong parsing to array.");
            std::process::exit(1);
        });
        let last_edit = &edits[edits.len() - 1];

        if !last_edit["is_typo"].as_bool().unwrap_or(false)
            || last_edit["src"]["lang"].as_str().unwrap_or("") != "eng"
        {
            continue;
        }

        let mut source_text = last_edit["src"]["text"]
            .as_str()
            .unwrap_or_else(|| {
                eprintln!("Something went wrong parsing to string.");
                std::process::exit(1);
            })
            .to_string();
        let mut target_text = last_edit["tgt"]["text"]
            .as_str()
            .unwrap_or_else(|| {
                eprintln!("Something went wrong parsing to string.");
                std::process::exit(1);
            })
            .to_string();

        for c in special_chars {
            source_text = source_text.replace(c, " ");
            target_text = target_text.replace(c, " ");
        }

        source_text = source_text
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
            .join(" ");
        target_text = target_text
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
            .join(" ");

        if source_text.eq(&target_text) {
            continue;
        }

        'alphanum: for pair in source_text.chars().zip_longest(target_text.chars()) {
            match pair {
                Both(sc, tc) => {
                    if (!sc.is_ascii_alphanumeric() && !sc.is_whitespace())
                        || (!tc.is_ascii_alphanumeric() && !tc.is_whitespace())
                    {
                        removed.push(format!("__src_non_ascii__: {}", &source_text));
                        removed.push(format!("__tgt_non_ascii__: {}", &target_text));
                        continue 'objects;
                    }
                }
                Left(sc) => {
                    if (!sc.is_ascii_alphanumeric() && !sc.is_whitespace()) {
                        removed.push(format!("__src_non_ascii__: {}", &source_text));
                        continue 'objects;
                    }
                }
                Right(tc) => {
                    if (!tc.is_ascii_alphanumeric() && !tc.is_whitespace()) {
                        removed.push(format!("__tgt_non_ascii__: {}", &target_text));
                        continue 'objects;
                    }
                }
            }
        }

        'filter0x: for pair in source_text.split(' ').zip_longest(target_text.split(' ')) {
            match pair {
                Both(sw, tw) => {
                    if sw.starts_with("0x") || tw.starts_with("0x") {
                        removed.push(format!("__src__: {}", &source_text));
                        removed.push(format!("__tgt__: {}", &target_text));
                        continue 'objects;
                    }
                }
                Left(sw) => {
                    if sw.starts_with("0x") {
                        removed.push(format!("__src__: {}", &source_text));
                        continue 'objects;
                    }
                }
                Right(tw) => {
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

    let removed_path = match std::env::current_dir() {
        Ok(cur_dir) => {
            let cur_dir = cur_dir.join("../data/removed.txt");
            cur_dir
                .to_str()
                .unwrap_or_else(|| {
                    eprintln!("Problem converting PathBuf to str");
                    std::process::exit(1);
                })
                .to_owned()
        }
        Err(e) => return Err(format!("Problem reading current dir with error:\n{}", e)),
    };

    let removed = removed.join("\n");

    match std::fs::write(&removed_path, removed) {
        Ok(_) => {
            println!("Written to {}", &removed_path);
        }
        Err(e) => {
            return Err(format!(
                "Problem writing to removed file: {}, with error:\n{}",
                &removed_path, e
            ))
        }
    };

    Ok((source_lines, target_lines))
}
